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
            
            # Parse LLM scores and build index-based score map
            llm_scores = {}  # index -> score
            try:
                # Try to extract JSON from response (may be wrapped in markdown)
                content = response.content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                raw_scores = json.loads(content)

                if isinstance(raw_scores, list):
                    for s in raw_scores:
                        doc_id = str(s.get("document_id", ""))
                        score = float(s.get("relevance_score", 0))
                        # Match by "doc_N" or just "N" pattern (1-indexed)
                        for prefix in ["doc_", "doc", ""]:
                            stripped = doc_id.replace(prefix, "").strip()
                            if stripped.isdigit():
                                idx = int(stripped) - 1  # Convert to 0-indexed
                                if 0 <= idx < len(documents):
                                    llm_scores[idx] = score
                                break

                logger.info("LLM relevance scores parsed", count=len(llm_scores))
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                logger.warning("Failed to parse LLM relevance scores, using search scores", error=str(e))

            # Build final scores: prefer LLM scores, fall back to search scores
            def get_doc_score(idx: int, doc: dict) -> float:
                if idx in llm_scores:
                    return llm_scores[idx]
                return float(doc.get("relevance_score", 0) or 0)

            # Rank documents by score
            scored_docs = [(i, doc, get_doc_score(i, doc)) for i, doc in enumerate(documents[:10])]
            scored_docs.sort(key=lambda x: x[2], reverse=True)

            # Filter by minimum relevance threshold
            min_relevance = 0.3
            relevant_docs = [doc for _, doc, score in scored_docs if score >= min_relevance]

            # If LLM scoring filtered everything but we have search results, keep them
            if not relevant_docs and documents:
                logger.warning("All docs filtered by relevance, keeping top search results")
                relevant_docs = documents[:5]

            scores_summary = [{"index": i, "score": s} for i, _, s in scored_docs]

            return AgentResult(
                success=True,
                data={
                    "ranked_documents": relevant_docs,
                    "scores": scores_summary,
                    "has_relevant_docs": len(relevant_docs) > 0,
                    "top_score": scored_docs[0][2] if scored_docs else 0
                },
                metadata={
                    "total_documents": len(documents),
                    "relevant_count": len(relevant_docs),
                    "min_relevance_threshold": min_relevance,
                    "llm_scores_parsed": len(llm_scores)
                }
            )
            
        except Exception as e:
            logger.error("Relevance scoring error", error=str(e))
            return AgentResult(
                success=False,
                data={"ranked_documents": []},
                error=str(e)
            )

