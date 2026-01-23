"""Query API endpoints."""

from fastapi import APIRouter, HTTPException
from app.models.query import QueryRequest, QueryResponse
from app.agents.base import AgentContext
from app.agents.intent import IntentAnalysisAgent
from app.agents.extraction import ExtractionAgent
from app.agents.relevance import RelevanceAgent
from app.agents.generation import GenerationAgent
from app.agents.validation import ValidationAgent
from app.services.conversation_service import ConversationService
from app.config import settings
import time
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/api/queries", tags=["queries"])


@router.post("", response_model=QueryResponse)
async def submit_query(
    request: QueryRequest,
):
    """
    Submit a query and get an answer with citations.

    This endpoint orchestrates the agentic pipeline:
    1. Intent Analysis
    2. Document Extraction
    3. Relevance Scoring
    4. Answer Generation
    5. Validation
    """
    start_time = time.time()

    try:
        # Handle conversation
        conversation_service = ConversationService()
        conversation_id = request.conversation_id

        # Create conversation if not provided
        if not conversation_id:
            conversation_id = await conversation_service.create_conversation(
                location=request.location
            )

        # Get conversation history for context
        conversation_history = await conversation_service.format_conversation_history_for_llm(
            conversation_id,
            limit=10  # Last 10 messages for context
        )

        # Store user message
        await conversation_service.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.question
        )

        # Initialize agents
        intent_agent = IntentAnalysisAgent()
        extraction_agent = ExtractionAgent()
        relevance_agent = RelevanceAgent()
        generation_agent = GenerationAgent()
        validation_agent = ValidationAgent()

        # Create context with conversation history
        context = AgentContext(
            query=request.question,
            user_location=request.location,
            metadata={},
            conversation_history=conversation_history if conversation_history else None
        )

        # Step 1: Intent Analysis
        logger.info("Starting intent analysis", query=request.question)
        intent_result = await intent_agent.execute(context)
        if not intent_result.success:
            raise HTTPException(status_code=500, detail="Intent analysis failed")
        context.metadata["intent_analysis"] = intent_result.data

        # Step 2: Document Extraction
        logger.info("Extracting documents")
        extraction_result = await extraction_agent.execute(context)
        if not extraction_result.success:
            raise HTTPException(status_code=500, detail="Document extraction failed")
        context.metadata["extraction"] = extraction_result.data

        # Step 3: Relevance Scoring
        logger.info("Scoring relevance")
        relevance_result = await relevance_agent.execute(context)
        if not relevance_result.success:
            raise HTTPException(status_code=500, detail="Relevance scoring failed")
        context.metadata["relevance"] = relevance_result.data

        # Step 4: Answer Generation (will handle fallback if no documents found)
        logger.info("Generating answer")
        generation_result = await generation_agent.execute(context)
        if not generation_result.success:
            raise HTTPException(status_code=500, detail="Answer generation failed")
        context.metadata["generation"] = generation_result.data

        # Step 5: Validation
        logger.info("Validating answer")
        validation_result = await validation_agent.execute(context)
        if not validation_result.success:
            logger.warning("Validation failed but proceeding", issues=validation_result.data.get("issues", []))

        # Build response
        generation_data = generation_result.data
        processing_time = int((time.time() - start_time) * 1000)

        # Extract processing metadata
        extraction_data = extraction_result.data
        relevance_data = relevance_result.data

        # Get unique sources from documents
        documents = extraction_data.get("documents", [])
        sources_used = list(set([doc.get("source", "Unknown") for doc in documents if doc.get("source")]))

        # Determine if GPT fallback was used
        used_gpt_fallback = generation_result.metadata.get("fallback_used", False)
        sources_found_count = extraction_data.get("count", 0)

        # Store assistant message
        answer_text = generation_data.get("answer", "")
        await conversation_service.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=answer_text,
            metadata={
                "citations_count": len(generation_data.get("citations", [])),
                "confidence": generation_data.get("confidence", "medium")
            }
        )

        response = QueryResponse(
            answer=answer_text,
            citations=[
                {
                    "title": cit.get("title", ""),
                    "url": cit.get("url") or cit.get("source_url", "#"),
                    "excerpt": cit.get("excerpt", ""),
                    "source": cit.get("source", ""),
                    "published_date": cit.get("published_date"),
                    "relevance_score": cit.get("relevance_score")
                }
                for cit in generation_data.get("citations", [])
            ],
            inline_citations=generation_data.get("inline_citations", []),
            retrieval_flow=generation_data.get("retrieval_flow"),
            confidence=generation_data.get("confidence", "medium"),
            processing_time_ms=processing_time,
            conversation_id=conversation_id,
            metadata={
                "intent": intent_result.data,
                "intent_keywords": intent_result.data.get("keywords", []),
                "sources_searched": sources_used if sources_used else ["Colorado Public Utilities Commission", "Colorado Energy Office", "Colorado State Legislature"],
                "sources_found": sources_found_count,
                "sources_used": generation_data.get("documents_used", 0),
                "used_gpt_fallback": used_gpt_fallback,
                "search_method": extraction_result.metadata.get("search_method", "keyword"),
                "embeddings_available": extraction_result.metadata.get("embeddings_available", False),
                "validation": validation_result.data if validation_result.success else None,
                "processing_steps": {
                    "intent_analysis": {
                        "completed": True,
                        "intent": intent_result.data.get("intent", "general_query"),
                        "keywords": intent_result.data.get("keywords", [])
                    },
                    "source_search": {
                        "completed": True,
                        "sources_searched": sources_used if sources_used else ["Colorado Public Utilities Commission", "Colorado Energy Office", "Colorado State Legislature"],
                        "sources_found": sources_found_count
                    },
                    "answer_generation": {
                        "completed": True,
                        "used_gpt_fallback": used_gpt_fallback,
                        "sources_used": generation_data.get("documents_used", 0)
                    },
                    "validation": {
                        "completed": validation_result.success
                    }
                }
            }
        )

        logger.info(
            "Query processed",
            query=request.question,
            processing_time_ms=processing_time,
            citations_count=len(response.citations),
            confidence=response.confidence
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Query processing error", error=str(e), query=request.question)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )
