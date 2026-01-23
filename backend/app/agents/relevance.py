"""Relevance scoring agent."""

from typing import List, Dict, Any
from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.llm import get_llm
from app.llm.base import LLMMessage
import json
import structlog

logger = structlog.get_logger()


class RelevanceAgent(BaseAgent):
    """Scores and ranks document relevance to query."""
    
    def __init__(self):
        super().__init__(
            name="relevance",
            description="Scores document relevance and ranks them"
        )
        self.llm = get_llm()
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Score document relevance."""
        try:
            # Get extracted documents from context
            extraction_result = context.metadata.get("extraction", {})
            documents = extraction_result.get("documents", [])
            
            if not documents:
                return AgentResult(
                    success=True,
                    data={"ranked_documents": [], "has_relevant_docs": False}
                )
            
            # Score each document
            system_prompt = """You are an expert at evaluating document relevance to queries.
For each document, score its relevance (0.0 to 1.0) and explain why.
Consider:
- Direct answer to the question
- Recency of information
- Authority of source
- Specificity to the query

Respond with JSON array:
[
    {
        "document_id": "doc_1",
        "relevance_score": 0.95,
        "reason": "Directly addresses the question about solar panel installation",
        "confidence": "high"
    }
]"""

            # Prepare documents for scoring
            docs_text = "\n\n".join([
                f"Document {i+1}:\nTitle: {doc.get('title', 'Unknown')}\n"
                f"Excerpt: {doc.get('excerpt', '')[:200]}..."
                for i, doc in enumerate(documents[:10])  # Limit to top 10
            ])
            
            user_prompt = f"""Query: {context.query}

Documents to score:
{docs_text}

Score each document's relevance to the query."""

            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_prompt)
            ]
            
            response = await self.llm.chat_completion(
                messages=messages,
                temperature=0.2,
                max_tokens=1000
            )
            
            # Parse scores
            try:
                scores = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback: use existing scores
                scores = [
                    {
                        "document_id": doc.get("id", f"doc_{i}"),
                        "relevance_score": doc.get("relevance_score", 0.5),
                        "reason": "Automated scoring",
                        "confidence": "medium"
                    }
                    for i, doc in enumerate(documents)
                ]
            
            # Rank documents by score
            ranked = sorted(
                documents,
                key=lambda d: next(
                    (s["relevance_score"] for s in scores if s["document_id"] == d.get("id")),
                    d.get("relevance_score", 0)
                ),
                reverse=True
            )
            
            # Filter by minimum relevance threshold
            min_relevance = 0.3
            relevant_docs = [
                doc for doc in ranked
                if next(
                    (s["relevance_score"] for s in scores if s["document_id"] == doc.get("id")),
                    doc.get("relevance_score", 0)
                ) >= min_relevance
            ]
            
            return AgentResult(
                success=True,
                data={
                    "ranked_documents": relevant_docs,
                    "scores": scores,
                    "has_relevant_docs": len(relevant_docs) > 0,
                    "top_score": scores[0]["relevance_score"] if scores else 0
                },
                metadata={
                    "total_documents": len(documents),
                    "relevant_count": len(relevant_docs),
                    "min_relevance_threshold": min_relevance
                }
            )
            
        except Exception as e:
            logger.error("Relevance scoring error", error=str(e))
            return AgentResult(
                success=False,
                data={"ranked_documents": []},
                error=str(e)
            )

