"""Base scraper class."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import hashlib
import structlog

logger = structlog.get_logger()


class ScrapedDocument(BaseModel):
    """Model for scraped documents."""
    title: str
    content: str
    source_url: str
    document_type: str  # 'regulation', 'order', 'guidance', etc.
    published_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    source: str  # 'CPUC', 'CEO', 'Legislature', etc.
    metadata: Dict[str, Any] = {}
    
    def get_checksum(self) -> str:
        """Generate checksum for duplicate detection."""
        content_hash = hashlib.sha256(
            f"{self.source_url}{self.title}".encode()
        ).hexdigest()
        return content_hash


class BaseScraper(ABC):
    """Base class for all scrapers."""
    
    def __init__(self, source_name: str, base_url: str):
        """
        Initialize scraper.
        
        Args:
            source_name: Name of the source (e.g., 'CPUC')
            base_url: Base URL for the source
        """
        self.source_name = source_name
        self.base_url = base_url
        logger.info("Scraper initialized", source=source_name, url=base_url)
    
    @abstractmethod
    async def scrape(self) -> List[ScrapedDocument]:
        """
        Scrape documents from the source.
        
        Returns:
            List of scraped documents
        """
        pass
    
    @abstractmethod
    def get_source_urls(self) -> List[str]:
        """
        Get list of URLs to scrape.
        
        Returns:
            List of URLs
        """
        pass

