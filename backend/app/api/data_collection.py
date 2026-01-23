"""Data collection API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.services.data_collection import DataCollectionService
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/api/data", tags=["data-collection"])


@router.post("/collect")
async def collect_data(
    background_tasks: BackgroundTasks,
    jurisdiction: str = "colorado"
):
    """
    Trigger data collection from all sources.
    
    This runs in the background to avoid blocking the API.
    """
    try:
        service = DataCollectionService()
        
        # Run in background
        background_tasks.add_task(service.collect_all_sources, jurisdiction)
        
        return {
            "status": "started",
            "message": "Data collection started in background",
            "jurisdiction": jurisdiction
        }
    except Exception as e:
        logger.error("Error starting data collection", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collect/{source}")
async def collect_source(
    source: str,
    background_tasks: BackgroundTasks,
    jurisdiction: str = "colorado"
):
    """
    Collect data from a specific source.
    
    Args:
        source: Source name (e.g., "CPUC")
        jurisdiction: Jurisdiction (default: "colorado")
    """
    try:
        service = DataCollectionService()
        
        # Run in background
        background_tasks.add_task(service.collect_source, source, jurisdiction)
        
        return {
            "status": "started",
            "message": f"Data collection from {source} started in background",
            "source": source,
            "jurisdiction": jurisdiction
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Error starting data collection", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats(jurisdiction: str = "colorado"):
    """Get data collection statistics."""
    try:
        from app.services.document_service import DocumentService
        service = DocumentService()
        
        count = await service.get_document_count(jurisdiction)
        
        return {
            "jurisdiction": jurisdiction,
            "document_count": count,
            "sources": ["CPUC"]  # TODO: Add other sources
        }
    except Exception as e:
        logger.error("Error getting stats", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

