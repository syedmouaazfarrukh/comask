"""Document storage and retrieval service using PostgreSQL + pgvector."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.db.models import Document, DocumentChunk, AuthorityLevel, JurisdictionType
from app.services.vector_search_service import VectorSearchService
from app.llm.embeddings import get_embeddings, embeddings_available
from app.scrapers.base import ScrapedDocument
import structlog

logger = structlog.get_logger()


class DocumentService:
    """Service for storing and retrieving documents using PostgreSQL."""

    def __init__(self):
        # Embeddings may not be available if API key not configured
        self.embeddings = get_embeddings()

    async def store_document(
        self,
        scraped_doc: ScrapedDocument,
        jurisdiction: str = "colorado",
        authority_level: AuthorityLevel = AuthorityLevel.STATE
    ) -> Optional[str]:
        """
        Store a scraped document in PostgreSQL with embeddings.

        Args:
            scraped_doc: Scraped document
            jurisdiction: Jurisdiction string
            authority_level: Authority level enum

        Returns:
            Document ID if successful, None otherwise
        """
        try:
            async with get_db_session() as session:
                # Generate document ID from checksum
                doc_checksum = scraped_doc.get_checksum()

                # Check if document already exists
                result = await session.execute(
                    select(Document).where(Document.checksum == doc_checksum)
                )
                existing = result.scalar_one_or_none()

                if existing:
                    logger.debug("Document already exists", doc_id=str(existing.id), title=scraped_doc.title)
                    return str(existing.id)

                # Map jurisdiction string to enum
                jurisdiction_map = {
                    "federal": JurisdictionType.FEDERAL,
                    "colorado": JurisdictionType.COLORADO,
                    "texas": JurisdictionType.TEXAS,
                    "nerc": JurisdictionType.NERC,
                    "wecc": JurisdictionType.WECC,
                    "spp": JurisdictionType.SPP,
                    "ercot": JurisdictionType.ERCOT,
                }
                jurisdiction_type = jurisdiction_map.get(jurisdiction.lower(), JurisdictionType.COLORADO)

                # Create document
                document = Document(
                    title=scraped_doc.title,
                    content=scraped_doc.content,
                    source_url=scraped_doc.source_url,
                    document_type=scraped_doc.document_type,
                    source=scraped_doc.source,
                    published_date=scraped_doc.published_date,
                    effective_date=scraped_doc.effective_date,
                    checksum=doc_checksum,
                    jurisdiction=jurisdiction_type,
                    authority_level=authority_level,
                    metadata=scraped_doc.metadata or {},
                )

                session.add(document)
                await session.flush()  # Get the document ID

                # Create chunks and embeddings
                try:
                    chunks = self._chunk_document(scraped_doc.content)

                    for i, chunk_text in enumerate(chunks):
                        # Generate embedding if available
                        embedding = None
                        if self.embeddings is not None:
                            try:
                                embedding = await self.embeddings.generate(chunk_text)
                            except Exception as embed_error:
                                logger.debug("Embedding generation failed for chunk", error=str(embed_error))

                        chunk = DocumentChunk(
                            document_id=document.id,
                            content=chunk_text,
                            chunk_index=i,
                            embedding=embedding,
                            metadata={"chunk_index": i, "total_chunks": len(chunks)}
                        )
                        session.add(chunk)

                    logger.debug("Created document chunks", doc_id=str(document.id), chunks=len(chunks))

                except Exception as e:
                    # If chunking fails, store document without chunks
                    logger.warning("Failed to create chunks, storing document without", error=str(e))

                await session.commit()

                logger.info("Document stored", doc_id=str(document.id), title=scraped_doc.title[:50])
                return str(document.id)

        except Exception as e:
            logger.error("Error storing document", error=str(e), title=scraped_doc.title)
            return None

    def _chunk_document(self, content: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split document content into overlapping chunks."""
        if len(content) <= chunk_size:
            return [content]

        chunks = []
        start = 0

        while start < len(content):
            end = start + chunk_size

            # Try to break at a sentence or paragraph boundary
            if end < len(content):
                # Look for sentence end
                for sep in ['. ', '.\n', '\n\n', '\n', ' ']:
                    sep_pos = content.rfind(sep, start + chunk_size // 2, end)
                    if sep_pos != -1:
                        end = sep_pos + len(sep)
                        break

            chunks.append(content[start:end].strip())
            start = end - overlap

            if start >= len(content):
                break

        return chunks

    async def search_documents(
        self,
        query: str,
        jurisdiction: Optional[str] = None,
        limit: int = 10,
        use_vector_search: bool = True,
        query_embedding: Optional[List[float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for documents by query using pgvector.

        Args:
            query: Search query
            jurisdiction: Filter by jurisdiction
            limit: Maximum number of results
            use_vector_search: Whether to use vector search
            query_embedding: Pre-generated query embedding to avoid duplicate API calls

        Returns:
            List of matching documents
        """
        try:
            async with get_db_session() as session:
                # Map jurisdiction to enum
                jurisdiction_types = None
                if jurisdiction:
                    jurisdiction_map = {
                        "federal": [JurisdictionType.FEDERAL],
                        "colorado": [JurisdictionType.COLORADO],
                        "texas": [JurisdictionType.TEXAS],
                        "state": [JurisdictionType.COLORADO],
                        "regional": [JurisdictionType.NERC, JurisdictionType.WECC, JurisdictionType.SPP, JurisdictionType.ERCOT],
                        "ercot": [JurisdictionType.ERCOT],
                    }
                    jurisdiction_types = jurisdiction_map.get(jurisdiction.lower())

                # Use vector search service with db session
                vector_search = VectorSearchService(session)
                results = await vector_search.search(
                    query=query,
                    limit=limit,
                    jurisdictions=jurisdiction_types,
                    query_embedding=query_embedding,
                )

                # Convert to dict format
                return [
                    {
                        "id": str(r.document.id),
                        "chunk_id": str(r.chunk.id) if r.chunk else None,
                        "title": r.document.title,
                        "content": r.chunk.content if r.chunk else r.document.content,
                        "source_url": r.document.source_url,
                        "source": r.document.source_name,
                        "document_type": r.document.document_type.value if r.document.document_type else None,
                        "published_date": r.document.published_date.isoformat() if r.document.published_date else None,
                        "relevance_score": r.similarity_score,
                        "authority_level": r.document.authority_level.value if r.document.authority_level else None,
                        "excerpt": r.excerpt,
                    }
                    for r in results
                ]

        except Exception as e:
            logger.error("Error searching documents", error=str(e), query=query[:50])
            return []

    async def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    select(Document).where(Document.id == doc_id)
                )
                doc = result.scalar_one_or_none()

                if doc:
                    return {
                        "id": str(doc.id),
                        "title": doc.title,
                        "content": doc.content,
                        "source_url": doc.source_url,
                        "source": doc.source,
                        "document_type": doc.document_type,
                        "published_date": doc.published_date.isoformat() if doc.published_date else None,
                        "authority_level": doc.authority_level.value if doc.authority_level else None,
                        "jurisdiction": doc.jurisdiction.value if doc.jurisdiction else None,
                    }
                return None

        except Exception as e:
            logger.error("Error getting document", doc_id=doc_id, error=str(e))
            return None

    async def get_document_count(self, jurisdiction: Optional[str] = None) -> int:
        """Get total document count."""
        try:
            async with get_db_session() as session:
                query = select(func.count(Document.id))

                if jurisdiction:
                    jurisdiction_map = {
                        "federal": JurisdictionType.FEDERAL,
                        "colorado": JurisdictionType.COLORADO,
                        "texas": JurisdictionType.TEXAS,
                        "state": JurisdictionType.COLORADO,
                        "ercot": JurisdictionType.ERCOT,
                    }
                    jur_type = jurisdiction_map.get(jurisdiction.lower())
                    if jur_type:
                        query = query.where(Document.jurisdiction == jur_type)

                result = await session.execute(query)
                return result.scalar() or 0

        except Exception as e:
            logger.error("Error getting document count", error=str(e))
            return 0
