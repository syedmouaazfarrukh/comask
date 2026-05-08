"""Data collection API endpoints."""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.services.data_collection import DataCollectionService
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/api/data", tags=["data-collection"])

# Global task tracker - survives beyond HTTP request lifecycle
_collection_tasks: Dict[str, Dict[str, Any]] = {}


@router.post("/collect")
async def collect_data(jurisdiction: str = "colorado"):
    """
    Trigger data collection from all sources.

    Uses asyncio.create_task() to run independently of the HTTP request,
    surviving Azure's 230s gateway timeout. Check progress via GET /api/data/collect/status.
    """
    task_key = f"all_{jurisdiction}"

    if task_key in _collection_tasks and not _collection_tasks[task_key].get("done"):
        return {
            "status": "already_running",
            "message": f"Collection for {jurisdiction} is already in progress",
            "progress": _collection_tasks[task_key],
        }

    try:
        service = DataCollectionService(jurisdiction=jurisdiction)

        # Initialize progress tracker
        _collection_tasks[task_key] = {
            "done": False,
            "jurisdiction": jurisdiction,
            "started_at": datetime.now().isoformat(),
            "sources": [s.source_name for s in service.scrapers],
            "current_source": None,
            "stored": 0,
            "errors": 0,
            "log": [],
        }

        # Fire-and-forget task in the event loop
        asyncio.create_task(_run_collection(service, jurisdiction, task_key))

        return {
            "status": "started",
            "message": f"Data collection for {jurisdiction} started. Check GET /api/data/collect/status?jurisdiction={jurisdiction}",
            "task_key": task_key,
        }
    except Exception as e:
        logger.error("Error starting data collection", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collect/{source}")
async def collect_source(source: str, jurisdiction: str = "colorado"):
    """
    Collect data from a specific source.

    Runs as a fire-and-forget task. Check progress via GET /api/data/collect/status.
    """
    task_key = f"{source}_{jurisdiction}"

    if task_key in _collection_tasks and not _collection_tasks[task_key].get("done"):
        return {
            "status": "already_running",
            "message": f"Collection for {source} ({jurisdiction}) is already in progress",
            "progress": _collection_tasks[task_key],
        }

    try:
        service = DataCollectionService(jurisdiction=jurisdiction)

        _collection_tasks[task_key] = {
            "done": False,
            "jurisdiction": jurisdiction,
            "source": source,
            "started_at": datetime.now().isoformat(),
            "current_phase": "initializing",
            "stored": 0,
            "errors": 0,
            "log": [],
        }

        asyncio.create_task(_run_source_collection(service, source, jurisdiction, task_key))

        return {
            "status": "started",
            "message": f"Collection from {source} started. Check GET /api/data/collect/status?task={task_key}",
            "task_key": task_key,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Error starting data collection", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collect/status")
async def collection_status(task: Optional[str] = None, jurisdiction: Optional[str] = None):
    """
    Check progress of running or completed collection tasks.

    Args:
        task: Specific task key to check
        jurisdiction: Filter tasks by jurisdiction
    """
    if task:
        if task in _collection_tasks:
            return _collection_tasks[task]
        raise HTTPException(status_code=404, detail=f"Task '{task}' not found")

    if jurisdiction:
        filtered = {k: v for k, v in _collection_tasks.items() if v.get("jurisdiction") == jurisdiction}
        return {"tasks": filtered}

    return {"tasks": _collection_tasks}


async def _run_collection(service: DataCollectionService, jurisdiction: str, task_key: str):
    """Run full collection as a fire-and-forget task."""
    progress = _collection_tasks[task_key]

    for scraper in service.scrapers:
        source_name = scraper.source_name
        progress["current_source"] = source_name
        progress["log"].append(f"Starting {source_name}...")

        try:
            async for event in service.collect_source_streaming(source_name, jurisdiction):
                evt = event.get("event", "")
                if evt == "doc_stored":
                    progress["stored"] += 1
                elif evt == "doc_error":
                    progress["errors"] += 1
                elif evt == "scraped":
                    progress["log"].append(f"{source_name}: scraped {event.get('count', 0)} docs")
                elif evt == "source_done":
                    progress["log"].append(
                        f"{source_name}: stored {event.get('stored', 0)}, errors {event.get('errors', 0)}"
                    )
        except Exception as e:
            progress["errors"] += 1
            progress["log"].append(f"{source_name}: ERROR - {str(e)}")
            logger.error("Collection source failed", source=source_name, error=str(e))

        await asyncio.sleep(2)

    progress["done"] = True
    progress["completed_at"] = datetime.now().isoformat()
    progress["log"].append("All sources complete.")
    logger.info("Full collection complete", task_key=task_key, stored=progress["stored"], errors=progress["errors"])


async def _run_source_collection(service: DataCollectionService, source: str, jurisdiction: str, task_key: str):
    """Run single-source collection as a fire-and-forget task."""
    progress = _collection_tasks[task_key]

    try:
        async for event in service.collect_source_streaming(source, jurisdiction):
            evt = event.get("event", "")
            if evt == "scraping":
                progress["current_phase"] = "scraping"
            elif evt == "heartbeat":
                progress["current_phase"] = f"scraping ({event.get('elapsed_seconds', 0)}s)"
            elif evt == "scraped":
                progress["current_phase"] = "storing"
                progress["total_scraped"] = event.get("count", 0)
                progress["log"].append(f"Scraped {event.get('count', 0)} documents")
            elif evt == "doc_stored":
                progress["stored"] = event.get("stored_total", progress["stored"] + 1)
                progress["last_stored"] = event.get("title", "")
            elif evt == "doc_error":
                progress["errors"] += 1
            elif evt == "source_done":
                progress["log"].append(
                    f"Done: stored {event.get('stored', 0)}, errors {event.get('errors', 0)}"
                )
    except Exception as e:
        progress["errors"] += 1
        progress["log"].append(f"ERROR: {str(e)}")
        logger.error("Source collection failed", source=source, error=str(e))

    progress["done"] = True
    progress["completed_at"] = datetime.now().isoformat()
    logger.info("Source collection complete", task_key=task_key, stored=progress["stored"], errors=progress["errors"])


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


@router.post("/fix-urls")
async def fix_urls():
    """
    Fix broken URLs in the database.
    Changes direct PDF links to landing pages that work.
    """
    try:
        from sqlalchemy import select
        from app.db.database import get_db_session
        from app.db.models import Document

        # URL replacements: old_url -> new_url
        URL_FIXES = {
            # Colorado Legislature PDFs -> Landing pages
            "https://leg.colorado.gov/sites/default/files/images/olls/crs2021-title-40.pdf":
                "https://leg.colorado.gov/colorado-revised-statutes",
            "https://leg.colorado.gov/sites/default/files/images/olls/crs2023-title-40.pdf":
                "https://leg.colorado.gov/colorado-revised-statutes",
            # Colorado PUC E-Filing -> Search page
            "https://www.dora.state.co.us/pls/efi/EFI.Show_Filing?p_fil=G_930344":
                "https://www.dora.state.co.us/pls/efi/EFI_Search_UI.search",
            # FERC Order 2222 -> Federal Register (eLibrary times out)
            "https://www.ferc.gov/media/ferc-order-no-2222-fact-sheet":
                "https://www.federalregister.gov/documents/2020/09/22/2020-19858/participation-of-distributed-energy-resource-aggregations-in-markets-operated-by-regional",
            "https://elibrary.ferc.gov/eLibrary/search?q=order%202222":
                "https://www.federalregister.gov/documents/2020/09/22/2020-19858/participation-of-distributed-energy-resource-aggregations-in-markets-operated-by-regional",
            # NERC -> Main standards page (AllReliabilityStandards.aspx returns 404)
            "https://www.nerc.com/pa/Stand/Pages/ReliabilityStandards.aspx":
                "https://www.nerc.com/pa/Stand/Pages/default.aspx",
            "https://www.nerc.com/pa/Stand/Pages/AllReliabilityStandards.aspx":
                "https://www.nerc.com/pa/Stand/Pages/default.aspx",
        }

        async with get_db_session() as session:
            result = await session.execute(select(Document))
            documents = result.scalars().all()

            fixed = []
            for doc in documents:
                if doc.source_url in URL_FIXES:
                    old_url = doc.source_url
                    new_url = URL_FIXES[old_url]
                    doc.source_url = new_url
                    fixed.append({
                        "title": doc.title[:60],
                        "old_url": old_url,
                        "new_url": new_url
                    })

            if fixed:
                await session.commit()

            return {
                "status": "success",
                "fixed_count": len(fixed),
                "fixed_documents": fixed
            }

    except Exception as e:
        logger.error("Error fixing URLs", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search-test")
async def search_test(query: str = "renewable energy", jurisdiction: str = "texas", limit: int = 5):
    """
    Diagnostic endpoint: test document search directly with detailed debug info.
    """
    try:
        from app.services.document_service import DocumentService
        from app.services.vector_search_service import VectorSearchService
        from app.processing.embedder import Embedder
        from app.db.database import get_db_session
        from app.db.models import Document, DocumentChunk, JurisdictionType
        from sqlalchemy import select, func
        from sqlalchemy.orm import selectinload
        import numpy as np

        service = DocumentService()
        embedder = Embedder()
        debug_info = {}

        # Generate query embedding
        query_embedding = None
        embed_status = "unavailable"
        if embedder.is_available:
            try:
                query_embedding = await embedder.embed_text(query)
                embed_status = f"generated (dim={len(query_embedding)})"
            except Exception as e:
                embed_status = f"failed: {str(e)}"

        # Map jurisdiction
        jurisdiction_map = {
            "federal": [JurisdictionType.FEDERAL],
            "colorado": [JurisdictionType.COLORADO],
            "texas": [JurisdictionType.TEXAS],
            "ercot": [JurisdictionType.ERCOT],
        }
        jur_types = jurisdiction_map.get(jurisdiction.lower())
        debug_info["jurisdiction_filter"] = [j.name for j in jur_types] if jur_types else None

        # Direct vector search test
        vector_results_count = 0
        vector_error = None
        top_similarities = []

        if query_embedding:
            async with get_db_session() as session:
                try:
                    # Count matching chunks
                    count_stmt = (
                        select(func.count(DocumentChunk.id))
                        .join(Document)
                        .where(DocumentChunk.embedding.isnot(None))
                    )
                    if jur_types:
                        count_stmt = count_stmt.where(Document.jurisdiction_type.in_(jur_types))
                    result = await session.execute(count_stmt)
                    chunk_count = result.scalar()
                    debug_info["chunks_with_embeddings"] = chunk_count

                    # Load a small sample and test cosine similarity
                    sample_stmt = (
                        select(DocumentChunk)
                        .options(selectinload(DocumentChunk.document))
                        .join(Document)
                        .where(DocumentChunk.embedding.isnot(None))
                    )
                    if jur_types:
                        sample_stmt = sample_stmt.where(Document.jurisdiction_type.in_(jur_types))
                    sample_stmt = sample_stmt.limit(50)  # Sample 50

                    result = await session.execute(sample_stmt)
                    sample_chunks = result.scalars().all()
                    debug_info["sample_chunks_loaded"] = len(sample_chunks)

                    query_vec = np.array(query_embedding, dtype=np.float64).flatten()
                    query_norm = float(np.linalg.norm(query_vec))

                    for chunk in sample_chunks:
                        try:
                            chunk_vec = np.array(list(chunk.embedding), dtype=np.float64).flatten()
                            chunk_norm = float(np.linalg.norm(chunk_vec))
                            if chunk_norm > 0 and query_norm > 0:
                                sim = float(np.dot(query_vec, chunk_vec) / (float(query_norm) * chunk_norm))
                                top_similarities.append({
                                    "title": chunk.document.title[:60] if chunk.document else "?",
                                    "similarity": round(sim, 4),
                                    "embed_dim": len(list(chunk.embedding)) if chunk.embedding is not None else 0,
                                })
                        except Exception as e:
                            debug_info["chunk_sim_error"] = str(e)
                            break

                    top_similarities.sort(key=lambda x: x["similarity"], reverse=True)
                    debug_info["top_5_similarities"] = top_similarities[:5]
                    vector_results_count = sum(1 for s in top_similarities if s["similarity"] >= 0.5)

                except Exception as e:
                    vector_error = str(e)

        debug_info["vector_error"] = vector_error
        debug_info["vector_results_above_threshold"] = vector_results_count

        # Run the full search pipeline
        results = await service.search_documents(
            query=query,
            jurisdiction=jurisdiction,
            limit=limit,
            use_vector_search=query_embedding is not None,
            query_embedding=query_embedding
        )

        return {
            "query": query,
            "jurisdiction": jurisdiction,
            "embedding_status": embed_status,
            "results_count": len(results),
            "debug": debug_info,
            "results": [
                {
                    "id": r.get("id"),
                    "title": r.get("title", "?")[:80],
                    "source": r.get("source"),
                    "relevance_score": r.get("relevance_score"),
                    "authority_level": r.get("authority_level"),
                    "excerpt": r.get("excerpt", "")[:200],
                }
                for r in results
            ]
        }
    except Exception as e:
        logger.error("Search test error", error=str(e))
        import traceback
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{traceback.format_exc()}")


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
