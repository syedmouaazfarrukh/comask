"""Vector search service using pgvector."""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, and_, or_, func
from sqlalchemy.orm import selectinload
import structlog

from app.db.models import Document, DocumentChunk, AuthorityLevel, JurisdictionType
from app.llm.embeddings import generate_query_embedding, generate_embeddings_batch
from app.config import settings

logger = structlog.get_logger()


class SearchResult:
    """Result from vector search."""

    def __init__(
        self,
        document: Document,
        chunk: DocumentChunk,
        similarity_score: float,
        excerpt: str,
    ):
        self.document = document
        self.chunk = chunk
        self.similarity_score = similarity_score
        self.excerpt = excerpt

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "document_id": str(self.document.id),
            "title": self.document.title,
            "source_url": self.document.source_url,
            "source_name": self.document.source_name,
            "document_type": self.document.document_type.value if self.document.document_type else None,
            "authority_level": self.document.authority_level.value if self.document.authority_level else None,
            "jurisdiction_type": self.document.jurisdiction_type.value if self.document.jurisdiction_type else None,
            "citation": self.document.citation,
            "published_date": self.document.published_date.isoformat() if self.document.published_date else None,
            "excerpt": self.excerpt,
            "similarity_score": self.similarity_score,
            "chunk_id": str(self.chunk.id) if self.chunk else None,
            "section_title": self.chunk.section_title if self.chunk else None,
            "section_hierarchy": self.chunk.section_hierarchy if self.chunk else [],
            "external_references": self.document.external_references or [],
        }


class VectorSearchService:
    """Service for vector-based document search using pgvector."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self,
        query: str,
        limit: int = 10,
        jurisdictions: Optional[List[JurisdictionType]] = None,
        authority_levels: Optional[List[AuthorityLevel]] = None,
        document_types: Optional[List[str]] = None,
        min_similarity: float = 0.5,
        include_hybrid: bool = True,
        query_embedding: Optional[List[float]] = None,
    ) -> List[SearchResult]:
        """
        Search for documents using vector similarity.

        Args:
            query: Search query text
            limit: Maximum number of results
            jurisdictions: Filter by jurisdiction types
            authority_levels: Filter by authority levels
            document_types: Filter by document types
            min_similarity: Minimum similarity threshold (0-1)
            include_hybrid: Also do keyword search and combine results
            query_embedding: Pre-generated query embedding to avoid duplicate API calls

        Returns:
            List of search results ranked by relevance
        """
        try:
            # Use provided embedding or generate a new one
            if query_embedding is None:
                query_embedding = await generate_query_embedding(query)

            results = []
            # Only do vector search if we have embeddings
            if query_embedding:
                # Build the vector search query
                results = await self._vector_search(
                    query_embedding,
                    limit * 2,  # Get more for re-ranking
                    jurisdictions,
                    authority_levels,
                    document_types,
                    min_similarity,
                )

            # If hybrid search is enabled or no vector results, do keyword search
            if include_hybrid or not results:
                keyword_results = await self._keyword_search(
                    query,
                    limit,
                    jurisdictions,
                    authority_levels,
                    document_types,
                )
                # Merge results
                results = self._merge_results(results, keyword_results)

            # Re-rank by authority level and recency
            results = self._rerank_results(results)

            return results[:limit]

        except Exception as e:
            logger.error("Vector search failed", query=query[:50], error=str(e))
            # Fall back to keyword search only
            return await self._keyword_search(
                query,
                limit,
                jurisdictions,
                authority_levels,
                document_types,
            )

    async def _vector_search(
        self,
        query_embedding: List[float],
        limit: int,
        jurisdictions: Optional[List[JurisdictionType]],
        authority_levels: Optional[List[AuthorityLevel]],
        document_types: Optional[List[str]],
        min_similarity: float,
    ) -> List[SearchResult]:
        """Execute vector similarity search using numpy for cosine similarity."""
        import numpy as np
        from sqlalchemy.orm import selectinload

        results = []

        try:
            # Query chunks that have embeddings
            stmt = (
                select(DocumentChunk)
                .options(selectinload(DocumentChunk.document))
                .where(DocumentChunk.embedding.isnot(None))
            )

            # Add jurisdiction filter via join
            needs_join = jurisdictions or authority_levels or document_types
            if needs_join:
                stmt = stmt.join(Document)

            if jurisdictions:
                stmt = stmt.where(Document.jurisdiction_type.in_(jurisdictions))
            if authority_levels:
                stmt = stmt.where(Document.authority_level.in_(authority_levels))
            if document_types:
                stmt = stmt.where(Document.document_type.in_(document_types))

            result = await self.db.execute(stmt)
            chunks = result.scalars().all()

            logger.debug("Vector search found chunks with embeddings", count=len(chunks))

            if not chunks:
                return results

            # Calculate cosine similarity for each chunk
            query_vec = np.array(query_embedding)
            query_norm = np.linalg.norm(query_vec)

            if query_norm == 0:
                logger.warning("Query embedding has zero norm")
                return results

            scored_results = []
            for chunk in chunks:
                if chunk.embedding is not None:
                    chunk_vec = np.array(chunk.embedding)
                    chunk_norm = np.linalg.norm(chunk_vec)
                    if chunk_norm > 0:
                        similarity = float(np.dot(query_vec, chunk_vec) / (query_norm * chunk_norm))
                        if similarity >= min_similarity:
                            scored_results.append((chunk, similarity))

            # Sort by similarity descending and limit
            scored_results.sort(key=lambda x: x[1], reverse=True)
            scored_results = scored_results[:limit]

            # Build search results
            for chunk, similarity in scored_results:
                document = chunk.document
                if not document:
                    doc_result = await self.db.execute(
                        select(Document).where(Document.id == chunk.document_id)
                    )
                    document = doc_result.scalar_one_or_none()

                if document:
                    results.append(SearchResult(
                        document=document,
                        chunk=chunk,
                        similarity_score=similarity,
                        excerpt=chunk.content[:500] if chunk.content else "",
                    ))

            logger.info("Vector search completed", results_count=len(results), total_chunks=len(chunks))

        except Exception as e:
            logger.error("Vector search query failed", error=str(e))

        return results

    async def _keyword_search(
        self,
        query: str,
        limit: int,
        jurisdictions: Optional[List[JurisdictionType]],
        authority_levels: Optional[List[AuthorityLevel]],
        document_types: Optional[List[str]],
    ) -> List[SearchResult]:
        """Execute keyword-based search."""
        results = []

        # Build SQLAlchemy query
        stmt = select(DocumentChunk).join(Document)

        # Extract keywords from query (remove common stop words)
        stop_words = {'what', 'is', 'the', 'a', 'an', 'are', 'how', 'does', 'do', 'can',
                      'for', 'of', 'to', 'in', 'on', 'with', 'by', 'and', 'or', 'about'}
        keywords = [word.strip() for word in query.lower().split()
                    if len(word.strip()) > 2 and word.lower() not in stop_words]

        # Build search condition for each keyword
        if keywords:
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append(DocumentChunk.content.ilike(f"%{keyword}%"))
                keyword_conditions.append(Document.title.ilike(f"%{keyword}%"))
            search_condition = or_(*keyword_conditions)
            stmt = stmt.where(search_condition)
        else:
            # Fallback to original query if no keywords extracted
            search_condition = or_(
                DocumentChunk.content.ilike(f"%{query}%"),
                Document.title.ilike(f"%{query}%"),
            )
            stmt = stmt.where(search_condition)

        # Add filters
        if jurisdictions:
            stmt = stmt.where(Document.jurisdiction_type.in_(jurisdictions))

        if authority_levels:
            stmt = stmt.where(Document.authority_level.in_(authority_levels))

        if document_types:
            stmt = stmt.where(Document.document_type.in_(document_types))

        stmt = stmt.limit(limit)

        try:
            result = await self.db.execute(stmt)
            chunks = result.scalars().all()

            for chunk in chunks:
                doc_result = await self.db.execute(
                    select(Document).where(Document.id == chunk.document_id)
                )
                document = doc_result.scalar_one_or_none()

                if document:
                    # Calculate a simple relevance score based on keyword match
                    content_lower = (chunk.content or "").lower()
                    title_lower = (document.title or "").lower()

                    # Score based on keyword matches
                    score = 0.0
                    keywords_matched = 0

                    for keyword in keywords:
                        kw_lower = keyword.lower()
                        if kw_lower in title_lower:
                            score += 0.2
                            keywords_matched += 1
                        if kw_lower in content_lower:
                            score += 0.1
                            keywords_matched += 1
                            # Boost for multiple occurrences
                            score += min(0.1, content_lower.count(kw_lower) * 0.01)

                    # Boost score if multiple keywords matched
                    if keywords_matched > 1:
                        score *= (1 + keywords_matched * 0.1)

                    # Ensure minimum score for any match
                    if score == 0 and keywords_matched == 0:
                        score = 0.1  # At least matched something in ILIKE

                    results.append(SearchResult(
                        document=document,
                        chunk=chunk,
                        similarity_score=min(1.0, score),
                        excerpt=chunk.content[:500] if chunk.content else "",
                    ))

        except Exception as e:
            logger.error("Keyword search failed", error=str(e))

        return results

    def _merge_results(
        self,
        vector_results: List[SearchResult],
        keyword_results: List[SearchResult],
    ) -> List[SearchResult]:
        """Merge vector and keyword search results, removing duplicates."""
        seen_docs = set()
        merged = []

        # Add vector results first (higher priority)
        for result in vector_results:
            doc_id = str(result.document.id)
            if doc_id not in seen_docs:
                seen_docs.add(doc_id)
                merged.append(result)

        # Add keyword results that aren't duplicates
        for result in keyword_results:
            doc_id = str(result.document.id)
            if doc_id not in seen_docs:
                seen_docs.add(doc_id)
                merged.append(result)

        return merged

    def _rerank_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Re-rank results by authority level, recency, and similarity.

        Authority ranking (lower = higher authority):
        - FEDERAL: 1
        - STATE: 2
        - REGIONAL: 3
        - UTILITY: 4
        """

        def rank_key(result: SearchResult) -> Tuple[int, float, float]:
            # Authority level (lower = better)
            authority = 4
            if result.document.authority_level:
                authority = result.document.authority_level.value

            # Recency score (higher = more recent)
            recency = 0.0
            if result.document.published_date:
                from datetime import date
                days_old = (date.today() - result.document.published_date).days
                recency = max(0, 1.0 - (days_old / 365))  # Decay over a year

            # Combined score (higher = better)
            combined = result.similarity_score * 0.5 + recency * 0.3 + (1 - authority / 4) * 0.2

            return (authority, -combined, -result.similarity_score)

        return sorted(results, key=rank_key)

    async def index_document(
        self,
        document: Document,
        chunks: List[str],
        section_titles: Optional[List[str]] = None,
        section_hierarchies: Optional[List[List[str]]] = None,
    ) -> int:
        """
        Index a document by generating embeddings for its chunks.

        Args:
            document: Document to index
            chunks: List of text chunks
            section_titles: Optional titles for each chunk
            section_hierarchies: Optional hierarchy paths for each chunk

        Returns:
            Number of chunks indexed
        """
        if not chunks:
            return 0

        try:
            # Generate embeddings for all chunks
            embeddings = await generate_embeddings_batch(chunks)

            # Create chunk records
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                chunk = DocumentChunk(
                    document_id=document.id,
                    content=chunk_text,
                    chunk_index=i,
                    embedding=embedding,
                    section_title=section_titles[i] if section_titles and i < len(section_titles) else None,
                    section_hierarchy=section_hierarchies[i] if section_hierarchies and i < len(section_hierarchies) else [],
                    token_count=len(chunk_text.split()),  # Rough estimate
                )
                self.db.add(chunk)

            await self.db.flush()
            logger.info("Document indexed", document_id=str(document.id), chunks=len(chunks))
            return len(chunks)

        except Exception as e:
            logger.error("Document indexing failed", document_id=str(document.id), error=str(e))
            raise
