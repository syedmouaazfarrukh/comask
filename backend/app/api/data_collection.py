"""Data collection API endpoints."""

from datetime import datetime
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


@router.get("/audit")
async def audit_data():
    """
    Get full audit of all documents in the database.

    Returns detailed information about every document including:
    - Source name and URL
    - Jurisdiction and authority level
    - Published/effective dates
    - Chunk count and embedding status
    """
    try:
        from sqlalchemy import select, func
        from app.db.database import get_db_session
        from app.db.models import Document, DocumentChunk

        async with get_db_session() as session:
            # Get all documents with chunk counts
            result = await session.execute(
                select(
                    Document.id,
                    Document.title,
                    Document.source_url,
                    Document.source_name,
                    Document.jurisdiction_type,
                    Document.authority_level,
                    Document.document_type,
                    Document.published_date,
                    Document.effective_date,
                    Document.created_at,
                    func.count(DocumentChunk.id).label('chunk_count'),
                    func.count(DocumentChunk.embedding).filter(DocumentChunk.embedding.isnot(None)).label('embedded_chunks')
                )
                .outerjoin(DocumentChunk)
                .group_by(Document.id)
                .order_by(Document.source_name, Document.created_at)
            )

            documents = []
            sources_summary = {}

            for row in result:
                source = row.source_name or "Unknown"

                # Build document info
                doc_info = {
                    "id": str(row.id),
                    "title": row.title[:100] + "..." if row.title and len(row.title) > 100 else row.title,
                    "source_url": row.source_url,
                    "source_name": source,
                    "jurisdiction": row.jurisdiction_type.value if row.jurisdiction_type else None,
                    "authority_level": row.authority_level.value if row.authority_level else None,
                    "document_type": row.document_type.value if row.document_type else None,
                    "published_date": row.published_date.isoformat() if row.published_date else None,
                    "effective_date": row.effective_date.isoformat() if row.effective_date else None,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "chunk_count": row.chunk_count,
                    "embedded_chunks": row.embedded_chunks,
                    "has_embeddings": row.embedded_chunks > 0
                }
                documents.append(doc_info)

                # Update source summary
                if source not in sources_summary:
                    sources_summary[source] = {
                        "count": 0,
                        "jurisdictions": set(),
                        "authority_levels": set(),
                        "total_chunks": 0,
                        "total_embedded": 0
                    }
                sources_summary[source]["count"] += 1
                if row.jurisdiction_type:
                    sources_summary[source]["jurisdictions"].add(row.jurisdiction_type.value)
                if row.authority_level:
                    sources_summary[source]["authority_levels"].add(row.authority_level.value)
                sources_summary[source]["total_chunks"] += row.chunk_count
                sources_summary[source]["total_embedded"] += row.embedded_chunks

            # Convert sets to lists for JSON serialization
            for source in sources_summary:
                sources_summary[source]["jurisdictions"] = list(sources_summary[source]["jurisdictions"])
                sources_summary[source]["authority_levels"] = list(sources_summary[source]["authority_levels"])

            return {
                "total_documents": len(documents),
                "total_sources": len(sources_summary),
                "sources_summary": sources_summary,
                "documents": documents,
                "audit_timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        logger.error("Error running audit", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

