"""Base agent class for agentic framework."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()


class AgentContext(BaseModel):
    """Context passed between agents."""
    query: str
    user_location: str = "colorado"
    metadata: Dict[str, Any] = {}
    conversation_history: Optional[str] = None  # Formatted conversation history for LLM


class AgentResult(BaseModel):
    """Result from an agent execution."""
    success: bool
    data: Any
    metadata: Dict[str, Any] = {}
    error: Optional[str] = None


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize agent.
        
        Args:
            name: Agent name
            description: Agent description
        """
        self.name = name
        self.description = description
        logger.info("Agent initialized", agent=name, description=description)
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute agent logic.
        
        Args:
            context: Agent context with query and metadata
            
        Returns:
            AgentResult with execution results
        """
        pass
    
    def log_execution(self, context: AgentContext, result: AgentResult):
        """Log agent execution."""
        logger.info(
            "Agent execution",
            agent=self.name,
            query=context.query,
            success=result.success,
            metadata=result.metadata
        )

