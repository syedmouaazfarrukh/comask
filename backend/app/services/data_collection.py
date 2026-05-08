"""Data collection service for running scrapers and populating database."""

from typing import List, Dict, Any
from app.scrapers.cpuc import CPUCScraper
from app.scrapers.ecfr import ECFRScraper
from app.scrapers.colorado_crs import ColoradoCRSScraper
from app.services.document_service import DocumentService
from app.scrapers.base import ScrapedDocument
from app.db.models import AuthorityLevel
import structlog
import asyncio

logger = structlog.get_logger()


class DataCollectionService:
    """Service for collecting and storing regulatory data."""

    def __init__(self, jurisdiction: str = "colorado"):
        self.document_service = DocumentService()
        self.jurisdiction = jurisdiction
        self.scrapers = self._get_scrapers_for_jurisdiction(jurisdiction)

    def _get_scrapers_for_jurisdiction(self, jurisdiction: str):
        """Get scrapers appropriate for the given jurisdiction."""
        common_scrapers = [ECFRScraper()]  # Federal regs apply everywhere

        if jurisdiction == "texas":
            from app.scrapers.texas_statutes import TexasStatutesScraper
            from app.scrapers.puct import PUCTScraper
            from app.scrapers.ercot import ERCOTScraper
            return [PUCTScraper(), TexasStatutesScraper(), ERCOTScraper()] + common_scrapers
        else:
            # Default: Colorado
            return [CPUCScraper(), ColoradoCRSScraper()] + common_scrapers
    
    async def collect_all_sources(self, jurisdiction: str = "colorado") -> Dict[str, Any]:
        """
        Run all scrapers and store documents.
        
        Args:
            jurisdiction: Jurisdiction to collect data for
        
        Returns:
            Summary of collection results
        """
        results = {
            "total_documents": 0,
            "new_documents": 0,
            "updated_documents": 0,
            "errors": [],
            "sources": {}
        }
        
        for scraper in self.scrapers:
            source_name = scraper.source_name
            logger.info("Starting data collection", source=source_name, jurisdiction=jurisdiction)
            
            try:
                # Scrape documents
                scraped_docs = await scraper.scrape()
                logger.info("Documents scraped", source=source_name, count=len(scraped_docs))
                
                # Determine authority level based on source
                authority_level_map = {
                    "eCFR": AuthorityLevel.FEDERAL,
                    "CPUC": AuthorityLevel.STATE,
                    "Colorado CRS": AuthorityLevel.STATE,
                    "PUCT": AuthorityLevel.STATE,
                    "Texas Statutes": AuthorityLevel.STATE,
                    "ERCOT": AuthorityLevel.REGIONAL,
                }
                authority = authority_level_map.get(source_name, AuthorityLevel.STATE)

                # Determine jurisdiction based on source
                jurisdiction_for_source = "federal" if source_name == "eCFR" else jurisdiction

                # Store each document
                source_results = {
                    "scraped": len(scraped_docs),
                    "stored": 0,
                    "errors": 0
                }

                for doc in scraped_docs:
                    try:
                        doc_id = await self.document_service.store_document(
                            doc,
                            jurisdiction=jurisdiction_for_source,
                            authority_level=authority
                        )
                        if doc_id:
                            source_results["stored"] += 1
                            results["new_documents"] += 1
                        else:
                            source_results["errors"] += 1
                    except Exception as e:
                        logger.error("Error storing document", source=source_name, error=str(e))
                        source_results["errors"] += 1
                        results["errors"].append({
                            "source": source_name,
                            "error": str(e)
                        })
                
                results["sources"][source_name] = source_results
                results["total_documents"] += len(scraped_docs)
                
                # Rate limiting between sources
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error("Error collecting from source", source=source_name, error=str(e))
                results["errors"].append({
                    "source": source_name,
                    "error": str(e)
                })
                results["sources"][source_name] = {
                    "scraped": 0,
                    "stored": 0,
                    "errors": 1
                }
        
        logger.info("Data collection complete", **results)
        return results
    
    async def collect_source(self, source_name: str, jurisdiction: str = "colorado") -> Dict[str, Any]:
        """
        Collect data from a specific source.

        Args:
            source_name: Name of the source (e.g., "CPUC")
            jurisdiction: Jurisdiction to collect data for

        Returns:
            Collection results
        """
        scraper = None
        for s in self.scrapers:
            if s.source_name == source_name:
                scraper = s
                break

        if not scraper:
            raise ValueError(f"Scraper not found for source: {source_name}")

        logger.info("Collecting from source", source=source_name)
        scraped_docs = await scraper.scrape()

        stored_count = 0
        for doc in scraped_docs:
            doc_id = await self.document_service.store_document(doc, jurisdiction)
            if doc_id:
                stored_count += 1

        return {
            "source": source_name,
            "scraped": len(scraped_docs),
            "stored": stored_count
        }

    async def collect_source_streaming(self, source_name: str, jurisdiction: str = "colorado"):
        """
        Collect data from a source, yielding progress dicts as each document is processed.

        Used with StreamingResponse to keep the HTTP connection alive on Azure,
        preventing container restarts during long scrapes.

        Yields:
            Dict with event type and progress info
        """
        scraper = None
        for s in self.scrapers:
            if s.source_name == source_name:
                scraper = s
                break

        if not scraper:
            raise ValueError(f"Scraper not found for source: {source_name}")

        logger.info("Streaming collection from source", source=source_name, jurisdiction=jurisdiction)

        authority_level_map = {
            "eCFR": AuthorityLevel.FEDERAL,
            "CPUC": AuthorityLevel.STATE,
            "Colorado CRS": AuthorityLevel.STATE,
            "PUCT": AuthorityLevel.STATE,
            "Texas Statutes": AuthorityLevel.STATE,
            "ERCOT": AuthorityLevel.REGIONAL,
        }
        authority = authority_level_map.get(source_name, AuthorityLevel.STATE)
        jurisdiction_for_source = "federal" if source_name == "eCFR" else jurisdiction

        try:
            yield {"event": "scraping", "source": source_name, "message": f"Scraping {source_name}..."}

            # Scrape with heartbeat to keep connection alive during long scrapes
            scrape_task = asyncio.create_task(scraper.scrape())
            elapsed = 0
            heartbeat_interval = 15  # seconds

            while not scrape_task.done():
                try:
                    await asyncio.wait_for(asyncio.shield(scrape_task), timeout=heartbeat_interval)
                except asyncio.TimeoutError:
                    elapsed += heartbeat_interval
                    yield {"event": "heartbeat", "source": source_name, "elapsed_seconds": elapsed, "message": "Still scraping..."}

            scraped_docs = scrape_task.result()

            yield {"event": "scraped", "source": source_name, "count": len(scraped_docs)}

            stored = 0
            errors = 0
            for i, doc in enumerate(scraped_docs):
                try:
                    doc_id = await self.document_service.store_document(
                        doc,
                        jurisdiction=jurisdiction_for_source,
                        authority_level=authority
                    )
                    if doc_id:
                        stored += 1
                        yield {
                            "event": "doc_stored",
                            "source": source_name,
                            "index": i + 1,
                            "total": len(scraped_docs),
                            "title": doc.title[:80],
                            "stored_total": stored,
                        }
                    else:
                        errors += 1
                        yield {"event": "doc_error", "source": source_name, "index": i + 1, "title": doc.title[:80]}
                except Exception as e:
                    errors += 1
                    logger.error("Error storing document", source=source_name, error=str(e))
                    yield {"event": "doc_error", "source": source_name, "index": i + 1, "error": str(e)}

            yield {
                "event": "source_done",
                "source": source_name,
                "scraped": len(scraped_docs),
                "stored": stored,
                "errors": errors,
            }

        except Exception as e:
            logger.error("Error in streaming collection", source=source_name, error=str(e))
            yield {"event": "source_error", "source": source_name, "error": str(e)}

