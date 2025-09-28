"""Chat router entrypoint (basic flow)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .models.schemas import ChatMessageIn, ChatMessageOut, ConversationHistoryOut, ConversationHistoryItem
from .services.chat_service import process_message
from app.gateway.database import get_db
from .persistence import repository

router = APIRouter(prefix="/chat", tags=["AI-Chat"])

@router.get("/health")
async def chat_health():
    return {"status": "ok"}


@router.post("/message", response_model=ChatMessageOut)
async def post_chat_message(payload: ChatMessageIn, db: AsyncSession = Depends(get_db)):
    if not payload.message.strip():  # Redundant (schema validator) but defensive
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message cannot be blank")
    result = await process_message(
        db=db,
        user_id=None,  # TODO: integrate real auth user id
        enterprise_id=payload.enterprise_id,
        conversation_id=payload.conversation_id,
        message=payload.message,
    )
    return ChatMessageOut(**result)


@router.get("/{conversation_id}", response_model=ConversationHistoryOut)
async def get_conversation_history(conversation_id: int, db: AsyncSession = Depends(get_db)):
    conv = await repository.get_conversation(db, conversation_id)
    if conv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    msgs = await repository.list_conversation_messages(db, conversation_id)
    items = [ConversationHistoryItem(role=m.role, content=m.content_text or "") for m in msgs]
    return ConversationHistoryOut(conversation_id=conversation_id, messages=items)
