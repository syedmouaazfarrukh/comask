"""Document extraction agent."""

from typing import List, Dict, Any
from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.services.document_service import DocumentService
from app.processing.embedder import Embedder
import structlog
from typing import Optional
from datetime import datetime, timedelta

logger = structlog.get_logger()


class ExtractionAgent(BaseAgent):
    """Extracts relevant documents based on query and intent."""
    
    def __init__(self, db_session: Optional[any] = None):
        super().__init__(
            name="extraction",
            description="Extracts relevant documents from vector database"
        )
        self.document_service = DocumentService()
        self.embedder = Embedder()
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Extract relevant documents from database."""
        try:
            # Get intent from context
            intent_data = context.metadata.get("intent_analysis", {})
            keywords = intent_data.get("keywords", [])
            intent = intent_data.get("intent", "")
            is_followup = intent_data.get("is_followup", False)
            context_from_history = intent_data.get("context_from_history")

            # Build search query - combine original query with keywords
            search_query = context.query
            if keywords:
                # Add keywords to improve search
                search_query = f"{context.query} {' '.join(keywords[:5])}"

            # For follow-up questions, enhance search with context from history
            if is_followup and context_from_history:
                search_query = f"{search_query} {context_from_history}"
                logger.info("Enhanced search query with conversation context",
                           is_followup=is_followup,
                           context_added=context_from_history[:50] if context_from_history else None)
            
            # Determine jurisdiction from location
            jurisdiction = context.user_location.lower() if context.user_location else "colorado"
            
            # Check if embeddings are available and try to generate query embedding
            use_vector_search = self.embedder.is_available
            query_embedding = []

            if use_vector_search:
                try:
                    query_embedding = await self.embedder.embed_text(context.query)
                    logger.info("Query embedding generated via Voyage AI", dim=len(query_embedding))
                except Exception as embed_error:
                    logger.warning("Embedding generation failed - using keyword search", error=str(embed_error))
                    use_vector_search = False
                    query_embedding = []
            else:
                logger.debug("Voyage AI embeddings not configured - using keyword search")
            
            # Search documents using document service
            # Pass the pre-generated embedding to avoid duplicate API calls
            extracted_docs = await self.document_service.search_documents(
                query=search_query,
                jurisdiction=jurisdiction,
                limit=15,  # Get more documents for relevance scoring
                use_vector_search=use_vector_search,
                query_embedding=query_embedding if use_vector_search and query_embedding else None
            )
            
            # Filter by recency (last 48 hours if published_date available)
            # Note: This is a simplified check - in production, you'd want more sophisticated filtering
            recent_docs = []
            cutoff_date = datetime.utcnow() - timedelta(hours=48)
            
            for doc in extracted_docs:
                # If no published_date, include it (assume recent)
                if not doc.get("published_date"):
                    recent_docs.append(doc)
                    continue
                
                try:
                    pub_date = datetime.fromisoformat(doc["published_date"].replace("Z", "+00:00"))
                    if pub_date >= cutoff_date:
                        recent_docs.append(doc)
                except:
                    # If date parsing fails, include the document
                    recent_docs.append(doc)
            
            # If no recent docs, use all docs (better than nothing)
            if not recent_docs and extracted_docs:
                recent_docs = extracted_docs[:10]
            
            # Limit to top results
            extracted_docs = recent_docs[:10]
            
            logger.info(
                "Documents extracted",
                query=context.query[:50],
                total_found=len(extracted_docs),
                jurisdiction=jurisdiction,
                vector_search=use_vector_search
            )
            
            return AgentResult(
                success=True,
                data={
                    "documents": extracted_docs,
                    "count": len(extracted_docs),
                    "query_embedding_dim": len(query_embedding) if query_embedding else 0
                },
                metadata={
                    "keywords_used": keywords,
                    "intent": intent,
                    "embeddings_available": use_vector_search,
                    "jurisdiction": jurisdiction,
                    "search_method": "vector" if use_vector_search else "keyword",
                    "is_followup": is_followup,
                    "context_enhanced": bool(is_followup and context_from_history)
                }
            )
            
        except Exception as e:
            logger.error("Extraction error", error=str(e), query=context.query)
            return AgentResult(
                success=False,
                data={"documents": [], "count": 0},
                error=str(e)
            )

