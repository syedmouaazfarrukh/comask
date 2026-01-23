"""Script to run scrapers and process documents."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.scrapers.cpuc import CPUCScraper
from app.processing.pipeline import ProcessingPipeline
from app.db.database import AsyncSessionLocal, init_db
import structlog

logger = structlog.get_logger()


async def main():
    """Run scrapers and process documents."""
    logger.info("Starting scraper run")
    
    # Initialize database
    await init_db()
    
    # Initialize scrapers
    scrapers = [
        CPUCScraper(),
        # Add more scrapers here
    ]
    
    all_documents = []
    
    # Run scrapers
    for scraper in scrapers:
        try:
            logger.info("Running scraper", source=scraper.source_name)
            documents = await scraper.scrape()
            all_documents.extend(documents)
            logger.info("Scraper complete", source=scraper.source_name, count=len(documents))
        except Exception as e:
            logger.error("Scraper failed", source=scraper.source_name, error=str(e))
    
    # Process documents
    if all_documents:
        async with AsyncSessionLocal() as db:
            pipeline = ProcessingPipeline(db)
            processed = await pipeline.process_documents(all_documents)
            logger.info("Processing complete", processed=processed)
    else:
        logger.warning("No documents scraped")
    
    logger.info("Scraper run complete")


if __name__ == "__main__":
    asyncio.run(main())

