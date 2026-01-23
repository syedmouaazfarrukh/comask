"""SQLAlchemy database models with pgvector support."""

from sqlalchemy import (
    Column, String, Text, Date, DateTime, Integer, Float, JSON,
    ForeignKey, Index, Boolean, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid
import enum

from app.db.database import Base
from app.config import settings


class AuthorityLevel(enum.Enum):
    """Authority level for documents (lower number = higher authority)."""
    FEDERAL = 1
    STATE = 2
    REGIONAL = 3
    UTILITY = 4


class JurisdictionType(enum.Enum):
    """Jurisdiction type for documents."""
    FEDERAL = "federal"
    COLORADO = "colorado"
    NERC = "nerc"
    WECC = "wecc"
    SPP = "spp"
    UTILITY = "utility"


class DocumentType(enum.Enum):
    """Document type classification."""
    REGULATION = "regulation"
    STATUTE = "statute"
    ORDER = "order"
    DECISION = "decision"
    STANDARD = "standard"
    TARIFF = "tariff"
    GUIDANCE = "guidance"
    RULE = "rule"
    OTHER = "other"


class User(Base):
    """User model with authentication support."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    queries = relationship("Query", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")


class RefreshToken(Base):
    """Refresh token storage for JWT authentication."""
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")


class Jurisdiction(Base):
    """Jurisdiction model (federal, state, regional, etc.)."""
    __tablename__ = "jurisdictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    level = Column(String(50), nullable=False)  # 'federal', 'state', 'regional', etc.
    code = Column(String(50))
    parent_id = Column(UUID(as_uuid=True), ForeignKey("jurisdictions.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Document(Base):
    """Document model for regulations and policies."""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    source_url = Column(Text, nullable=False)
    content = Column(Text)  # Full document content
    document_type = Column(
        Enum(DocumentType),
        default=DocumentType.OTHER
    )

    # Authority and jurisdiction
    authority_level = Column(
        Enum(AuthorityLevel),
        default=AuthorityLevel.STATE,
        nullable=False
    )
    jurisdiction_type = Column(
        Enum(JurisdictionType),
        default=JurisdictionType.COLORADO,
        nullable=False
    )

    # Source identification
    source_name = Column(String(255))  # e.g., "Colorado PUC", "eCFR", "FERC"
    docket_number = Column(String(100))  # For PUC/FERC documents
    citation = Column(String(255))  # Official citation format

    # Dates
    published_date = Column(Date)
    effective_date = Column(Date)
    expiration_date = Column(Date)

    # Status and tracking
    status = Column(String(50), default="active")  # 'active', 'proposed', 'repealed', 'superseded'
    checksum = Column(String(64), unique=True)
    file_path = Column(Text)

    # External references (NEC, IEEE, etc.)
    external_references = Column(JSON, default=list)  # List of external standard references

    # Additional metadata
    document_metadata = Column(JSON, default=dict)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    versions = relationship("DocumentVersion", back_populates="document")

    __table_args__ = (
        Index("idx_documents_published", "published_date"),
        Index("idx_documents_status", "status"),
        Index("idx_documents_type", "document_type"),
        Index("idx_documents_authority", "authority_level"),
        Index("idx_documents_jurisdiction", "jurisdiction_type"),
        Index("idx_documents_source", "source_name"),
    )


class DocumentChunk(Base):
    """Document chunk with vector embedding for semantic search."""
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)

    # Chunk content
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order within document

    # Vector embedding (Voyage AI dimension = 1024)
    embedding = Column(Vector(settings.vector_dimension))

    # Context for better retrieval
    section_title = Column(String(500))  # Section header if available
    section_hierarchy = Column(JSON, default=list)  # ["Title 40", "Part 1", "Section 1.1"]

    # Token count for tracking
    token_count = Column(Integer)

    # Metadata
    chunk_metadata = Column(JSON, default=dict)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="chunks")

    __table_args__ = (
        Index("idx_chunks_document", "document_id"),
        Index("idx_chunks_embedding", "embedding", postgresql_using="hnsw",
              postgresql_ops={"embedding": "vector_cosine_ops"}),
    )


class DocumentVersion(Base):
    """Document version for change tracking."""
    __tablename__ = "document_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text)
    file_path = Column(Text)
    checksum = Column(String(64))
    version_number = Column(Integer, nullable=False)
    change_summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="versions")


class Conversation(Base):
    """Conversation session for multi-turn queries."""
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(255))  # Auto-generated from first query
    location = Column(String(100), default="Colorado")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="conversations")
    queries = relationship("Query", back_populates="conversation", order_by="Query.created_at")


class Query(Base):
    """User query model with enhanced metadata."""
    __tablename__ = "queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"))

    # Query and response
    question = Column(Text, nullable=False)
    answer = Column(Text)

    # Confidence scoring
    confidence_level = Column(String(20))  # 'high', 'medium', 'low'
    confidence_score = Column(Float)  # 0.0 - 1.0
    confidence_factors = Column(JSON, default=dict)  # Breakdown of confidence factors

    # Source lineage for knowledge graph
    source_graph_data = Column(JSON, default=dict)  # React Flow compatible graph data

    # Processing metadata
    processing_time_ms = Column(Integer)
    intent_analysis = Column(JSON)  # Results from intent agent
    model_used = Column(String(100))  # Which Claude model was used

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="queries")
    conversation = relationship("Conversation", back_populates="queries")
    citations = relationship("Citation", back_populates="query", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_queries_user", "user_id", "created_at"),
        Index("idx_queries_conversation", "conversation_id"),
    )


class Citation(Base):
    """Citation model for query answers with enhanced metadata."""
    __tablename__ = "citations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("queries.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id", ondelete="SET NULL"))

    # Citation content
    excerpt = Column(Text)

    # Scoring
    relevance_score = Column(Float)
    similarity_score = Column(Float)  # Vector similarity

    # Position tracking
    claim_text = Column(Text)  # The claim this citation supports
    position_in_answer = Column(Integer)  # Order in the answer

    # Source metadata snapshot (for historical accuracy)
    source_title = Column(Text)
    source_url = Column(Text)
    source_citation = Column(String(255))  # Official citation format
    authority_level = Column(String(50))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    query = relationship("Query", back_populates="citations")

    __table_args__ = (
        Index("idx_citations_query", "query_id"),
        Index("idx_citations_document", "document_id"),
    )
