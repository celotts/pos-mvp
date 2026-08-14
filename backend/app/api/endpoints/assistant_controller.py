from typing import Any

from api.deps import get_db
from fastapi import APIRouter, Depends
from modules.ai_service import ai_service
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])
db_dependency = Depends(get_db)


class ChatQuery(BaseModel):
    question: str


@router.post("/chat")
async def handle_chat(
    query: ChatQuery,
    db: AsyncSession = db_dependency,
) -> Any:
    """
    Endpoint para interactuar con el Asistente de Inteligencia de Negocio.
    Recibe una pregunta en lenguaje natural y devuelve una respuesta generada por IA.
    """
    # Aquí llamaremos a la lógica principal del asistente de IA
    response_text = await ai_service.get_rag_response(db=db, query=query.question)

    return {"answer": response_text}
