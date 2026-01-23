"""Data processing pipeline."""

from typing import List
from app.scrapers.base import ScrapedDocument
from app.processing.embedder import Embedder
from app.db.models import Document, DocumentVersion
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import structlog

logger = structlog.get_logger()


class ProcessingPipeline:
    """Processes scraped documents through categorization and embedding."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.embedder = Embedder()
    
    async def process_documents(self, scraped_docs: List[ScrapedDocument]) -> int:
        """
        Process scraped documents.
        
        Args:
            scraped_docs: List of scraped documents
            
        Returns:
            Number of documents processed
        """
        processed_count = 0
        
        for doc in scraped_docs:
            try:
                # Check for duplicates
                existing = await self._check_duplicate(doc)
                if existing:
                    logger.debug("Skipping duplicate document", url=doc.source_url)
                    continue
                
                # Categorize document
                category = self._categorize_document(doc)
                
                # Create database document
                db_doc = Document(
                    title=doc.title,
                    source_url=doc.source_url,
                    document_type=doc.document_type or category,
                    published_date=doc.published_date,
                    effective_date=doc.effective_date,
                    status="active",
                    checksum=doc.get_checksum(),
                    document_metadata=doc.metadata  # ScrapedDocument.metadata -> Document.document_metadata
                )
                
                self.db.add(db_doc)
                await self.db.flush()
                
                # Create document version
                doc_version = DocumentVersion(
                    document_id=db_doc.id,
                    content=doc.content,
                    version_number=1,
                    checksum=doc.get_checksum()
                )
                
                self.db.add(doc_version)
                
                # Generate embeddings (for vector search)
                # This would be stored in vector DB
                # For now, we'll just log it
                embedding = await self.embedder.embed_text(doc.content[:1000])  # First 1000 chars
                logger.debug("Generated embedding", doc_id=str(db_doc.id), dim=len(embedding))
                
                processed_count += 1
                
            except Exception as e:
                logger.error("Error processing document", error=str(e), url=doc.source_url)
                continue
        
        await self.db.commit()
        logger.info("Processing complete", processed=processed_count, total=len(scraped_docs))
        return processed_count
    
    async def _check_duplicate(self, doc: ScrapedDocument) -> bool:
        """Check if document already exists."""
        checksum = doc.get_checksum()
        # TODO: Query database for existing document with same checksum
        return False
    
    def _categorize_document(self, doc: ScrapedDocument) -> str:
        """Categorize document based on content and metadata."""
        # Simple categorization logic
        content_lower = doc.content.lower()
        
        if any(word in content_lower for word in ['regulation', 'rule', 'standard']):
            return 'regulation'
        elif any(word in content_lower for word in ['order', 'decision']):
            return 'order'
        elif any(word in content_lower for word in ['guidance', 'guideline']):
            return 'guidance'
        elif any(word in content_lower for word in ['bill', 'statute', 'law']):
            return 'legislation'
        else:
            return 'document'

