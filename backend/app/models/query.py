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


class InlineCitation(BaseModel):
    """Inline citation linking a specific fact to its source."""
    id: str = Field(..., description="Unique identifier for this inline citation (e.g., 'cite-1')")
    fact: str = Field(..., description="The specific fact, number, or claim being cited")
    source_index: int = Field(..., description="Index of the source document (0-based)")
    source_title: str = Field(..., description="Title of the source document")
    source_excerpt: str = Field(..., description="The exact excerpt from the source that supports this fact")
    source_url: Optional[str] = Field(None, description="URL to the source document")


class RetrievalFlowNode(BaseModel):
    """A node in the retrieval flow for knowledge graph visualization."""
    id: str
    type: str = Field(..., description="'query', 'document', 'answer', or 'chunk'")
    label: str
    metadata: Optional[dict] = None


class RetrievalFlowEdge(BaseModel):
    """An edge in the retrieval flow."""
    source: str
    target: str
    label: Optional[str] = None
    relevance_score: Optional[float] = None


class RetrievalFlow(BaseModel):
    """The complete retrieval flow for knowledge graph visualization."""
    nodes: List[RetrievalFlowNode] = []
    edges: List[RetrievalFlowEdge] = []


class QueryResponse(BaseModel):
    """Response model for queries."""
    answer: str
    citations: List[Citation] = []
    inline_citations: List[InlineCitation] = []
    retrieval_flow: Optional[RetrievalFlow] = None
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

