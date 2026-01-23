"""Intent analysis agent."""

from typing import Dict, Any
from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.llm import get_llm
from app.llm.base import LLMMessage
import json
import structlog

logger = structlog.get_logger()


class IntentAnalysisAgent(BaseAgent):
    """Analyzes user query intent and extracts key information."""
    
    def __init__(self):
        super().__init__(
            name="intent_analysis",
            description="Analyzes user queries to understand intent and extract key information"
        )
        self.llm = get_llm()
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Analyze query intent."""
        try:
            system_prompt = """You are an expert at analyzing energy regulation queries. 
Analyze the user's question and extract:
1. Primary intent (compliance_check, regulation_lookup, policy_question, etc.)
2. Key topics (solar, net_metering, permits, etc.)
3. Specific entities mentioned (utilities, agencies, etc.)
4. Question type (yes/no, how_to, what_is, etc.)
5. Jurisdiction level needed (state, federal, local)

Respond ONLY with valid JSON in this format:
{
    "intent": "compliance_check",
    "topics": ["solar", "residential"],
    "entities": ["CPUC"],
    "question_type": "yes_no",
    "jurisdiction": "state",
    "keywords": ["install", "solar panels", "residential"]
}"""

            user_prompt = f"Analyze this query about Colorado energy regulations: {context.query}"
            
            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_prompt)
            ]
            
            response = await self.llm.chat_completion(
                messages=messages,
                temperature=0.1,  # Low temperature for consistent analysis
                max_tokens=300
            )
            
            # Parse JSON response
            try:
                intent_data = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.warning("Failed to parse intent JSON, using fallback")
                intent_data = {
                    "intent": "general_query",
                    "topics": [],
                    "entities": [],
                    "question_type": "general",
                    "jurisdiction": "state",
                    "keywords": context.query.lower().split()
                }
            
            return AgentResult(
                success=True,
                data=intent_data,
                metadata={
                    "model": response.model,
                    "tokens": response.usage.get("total_tokens", 0) if response.usage else 0
                }
            )
            
        except Exception as e:
            logger.error("Intent analysis error", error=str(e), query=context.query)
            return AgentResult(
                success=False,
                data={},
                error=str(e)
            )

