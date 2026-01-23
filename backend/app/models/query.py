"""Pydantic models for queries."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for user queries."""
    question: str = Field(..., description="User's question", min_length=1)
    location: str = Field(default="colorado", description="User's location")
    context: Optional[dict] = Field(default=None, description="Additional context")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID for context")


class Citation(BaseModel):
    """Citation model."""
    title: str
    url: str
    excerpt: str
    source: str
    published_date: Optional[str] = None
    relevance_score: Optional[float] = None


class QueryResponse(BaseModel):
    """Response model for queries."""
    answer: str
    citations: List[Citation] = []
    confidence: str = Field(..., description="high, medium, or low")
    processing_time_ms: Optional[int] = None
    query_id: Optional[str] = None
    conversation_id: Optional[str] = None
    metadata: Optional[dict] = None


class ProcessingStep(BaseModel):
    """Processing step information."""
    step: str
    status: str
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)

