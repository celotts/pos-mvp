from typing import Any

from api.response_factory import create_api_response
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends
from models.user import User as UserModel
from modules.ai_service import ai_service
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)


class ChatQuery(BaseModel):
    question: str


@router.post("/chat")
async def handle_chat(
    query: ChatQuery,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Endpoint para interactuar con el Asistente de Inteligencia de Negocio."""
    response_text = await ai_service.get_rag_response(db=db, query=query.question)
    return create_api_response(data={"answer": response_text})
