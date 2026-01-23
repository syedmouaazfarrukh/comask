"""Answer validation agent."""

from typing import Dict, Any
from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.llm import get_llm
from app.llm.base import LLMMessage
import structlog

logger = structlog.get_logger()


class ValidationAgent(BaseAgent):
    """Validates that answers are grounded in source documents."""
    
    def __init__(self):
        super().__init__(
            name="validation",
            description="Validates answers are properly cited and grounded"
        )
        self.llm = get_llm()
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Validate answer quality and citations."""
        try:
            # Get generated answer from context
            generation_result = context.metadata.get("generation", {})
            answer = generation_result.get("answer", "")
            citations = generation_result.get("citations", [])
            documents = context.metadata.get("relevance", {}).get("ranked_documents", [])
            
            if not answer:
                return AgentResult(
                    success=False,
                    data={"valid": False, "issues": ["No answer generated"]}
                )
            
            # Check for citations
            has_citations = len(citations) > 0
            answer_has_citations = any(
                cit.get("title", "").lower() in answer.lower()
                for cit in citations
            )
            
            # Validate with LLM
            system_prompt = """You are a quality validator for regulatory answers. Check if:
1. The answer is grounded in the provided documents
2. Citations are present and accurate
3. No unsupported claims are made
4. Uncertainty is properly stated

Respond with JSON:
{
    "valid": true/false,
    "issues": ["list of issues if any"],
    "citation_quality": "good" | "needs_improvement" | "missing",
    "grounded": true/false
}"""

            documents_text = "\n".join([
                f"- {doc.get('title', 'Unknown')}: {doc.get('excerpt', '')[:150]}..."
                for doc in documents[:5]
            ])
            
            user_prompt = f"""Answer to validate:
{answer}

Citations provided: {len(citations)}
Available documents:
{documents_text}

Validate this answer."""

            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_prompt)
            ]
            
            response = await self.llm.chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse validation result
            import json
            try:
                validation = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback validation
                validation = {
                    "valid": has_citations and answer_has_citations,
                    "issues": [] if has_citations else ["Missing citations"],
                    "citation_quality": "good" if has_citations else "missing",
                    "grounded": True
                }
            
            # Add manual checks
            if not has_citations:
                validation["issues"].append("No citations provided")
            if not answer_has_citations:
                validation["issues"].append("Citations not referenced in answer")
            
            return AgentResult(
                success=True,
                data=validation,
                metadata={
                    "citations_count": len(citations),
                    "answer_length": len(answer)
                }
            )
            
        except Exception as e:
            logger.error("Validation error", error=str(e))
            return AgentResult(
                success=False,
                data={"valid": False, "issues": [f"Validation error: {str(e)}"]},
                error=str(e)
            )

