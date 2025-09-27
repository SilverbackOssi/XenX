"""Chat router entrypoint (placeholder)."""
from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["ai-chat"])

@router.get("/health")
async def chat_health():
    return {"status": "ok"}
