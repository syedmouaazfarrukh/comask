"""Conversation management API endpoints."""

from fastapi import APIRouter, HTTPException
from app.services.conversation_service import ConversationService
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("/create")
async def create_conversation(
    location: str = "colorado",
):
    """Create a new conversation."""
    try:
        conversation_service = ConversationService()
        conversation_id = await conversation_service.create_conversation(
            location=location
        )
        return {"conversation_id": conversation_id}
    except Exception as e:
        logger.error("Failed to create conversation", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
):
    """Delete a conversation and all its messages."""
    try:
        conversation_service = ConversationService()
        success = await conversation_service.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete conversation", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}/history")
async def get_conversation_history(
    conversation_id: str,
    limit: int = 50,
):
    """Get conversation history."""
    try:
        conversation_service = ConversationService()
        messages = await conversation_service.get_conversation_history(
            conversation_id,
            limit=limit
        )
        return {"messages": messages}
    except Exception as e:
        logger.error("Failed to get conversation history", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
