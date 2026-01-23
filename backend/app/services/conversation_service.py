"""Conversation service for managing chat conversations using PostgreSQL."""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.db.models import Conversation, Query
import structlog

logger = structlog.get_logger()


class ConversationService:
    """Service for managing conversations and messages using PostgreSQL."""

    async def create_conversation(
        self,
        user_id: Optional[str] = None,
        location: str = "colorado",
        title: Optional[str] = None
    ) -> str:
        """Create a new conversation and return its ID."""
        try:
            async with get_db_session() as session:
                conversation = Conversation(
                    user_id=uuid.UUID(user_id) if user_id else None,
                    title=title or "New Conversation",
                    metadata={"location": location}
                )

                session.add(conversation)
                await session.commit()

                logger.info("Conversation created", conversation_id=str(conversation.id), location=location)
                return str(conversation.id)

        except Exception as e:
            logger.error("Failed to create conversation", error=str(e))
            raise

    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a conversation by ID."""
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
                )
                conversation = result.scalar_one_or_none()

                if conversation:
                    return {
                        "id": str(conversation.id),
                        "user_id": str(conversation.user_id) if conversation.user_id else None,
                        "title": conversation.title,
                        "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
                        "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
                        "metadata": conversation.metadata or {}
                    }
                return None

        except Exception as e:
            logger.error("Failed to get conversation", error=str(e), conversation_id=conversation_id)
            return None

    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get conversation history (queries) for a conversation."""
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    select(Query)
                    .where(Query.conversation_id == uuid.UUID(conversation_id))
                    .order_by(Query.created_at.asc())
                    .limit(limit)
                )
                queries = result.scalars().all()

                messages = []
                for query in queries:
                    # Add user message
                    messages.append({
                        "id": str(query.id),
                        "conversation_id": str(query.conversation_id),
                        "role": "user",
                        "content": query.question,
                        "created_at": query.created_at.isoformat() if query.created_at else None
                    })
                    # Add assistant message if answer exists
                    if query.answer:
                        messages.append({
                            "id": f"{query.id}-response",
                            "conversation_id": str(query.conversation_id),
                            "role": "assistant",
                            "content": query.answer,
                            "created_at": query.created_at.isoformat() if query.created_at else None,
                            "metadata": {
                                "confidence_score": query.confidence_score,
                                "confidence_level": query.confidence_level,
                            }
                        })

                return messages

        except Exception as e:
            logger.error("Failed to get conversation history", error=str(e), conversation_id=conversation_id)
            return []

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a message (query) to a conversation."""
        try:
            async with get_db_session() as session:
                if role == "user":
                    # Create a new query for user messages
                    query = Query(
                        conversation_id=uuid.UUID(conversation_id),
                        question=content,
                        metadata=metadata or {}
                    )
                    session.add(query)
                    await session.commit()

                    # Update conversation
                    await session.execute(
                        update(Conversation)
                        .where(Conversation.id == uuid.UUID(conversation_id))
                        .values(updated_at=datetime.utcnow())
                    )
                    await session.commit()

                    logger.debug("Query added", conversation_id=conversation_id)
                    return str(query.id)
                else:
                    # For assistant messages, update the last query with the answer
                    result = await session.execute(
                        select(Query)
                        .where(Query.conversation_id == uuid.UUID(conversation_id))
                        .order_by(Query.created_at.desc())
                        .limit(1)
                    )
                    last_query = result.scalar_one_or_none()

                    if last_query:
                        last_query.answer = content
                        if metadata:
                            last_query.confidence_score = metadata.get("confidence_score")
                            last_query.confidence_level = metadata.get("confidence_level")
                        await session.commit()
                        return str(last_query.id)

                    return ""

        except Exception as e:
            logger.error("Failed to add message", error=str(e), conversation_id=conversation_id)
            raise

    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its queries."""
        try:
            async with get_db_session() as session:
                # Delete queries
                await session.execute(
                    delete(Query).where(Query.conversation_id == uuid.UUID(conversation_id))
                )

                # Delete conversation
                result = await session.execute(
                    delete(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
                )
                await session.commit()

                logger.info("Conversation deleted", conversation_id=conversation_id)
                return result.rowcount > 0

        except Exception as e:
            logger.error("Failed to delete conversation", error=str(e), conversation_id=conversation_id)
            return False

    async def format_conversation_history_for_llm(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> str:
        """Format conversation history as a string for LLM context."""
        messages = await self.get_conversation_history(conversation_id, limit)

        if not messages:
            return ""

        history_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_parts.append(f"{role.capitalize()}: {content}")

        return "\n\n".join(history_parts)


# Factory function for backward compatibility
async def get_conversation_service() -> ConversationService:
    """Get a ConversationService instance."""
    return ConversationService()
