from typing import Any

from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends
from models.user import User as UserModel
from modules.ai_service import ai_service
from schemas.assistant import ChatQuery, ChatResponseData  # Import new schemas
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)


@router.post(
    "/chat",
    response_model=ApiResponse[ChatResponseData],  # Specify the response model
    summary="Interact with the Business Intelligence AI Assistant",
    description="""
    Send a question in natural language to get insights about sales data.
    The assistant uses a RAG (Retrieval-Augmented Generation) pipeline
    to answer based on the information stored in the sales database.
    """,
)
async def handle_chat(
    query: ChatQuery,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Endpoint to interact with the Business Intelligence Assistant."""
    response_text = await ai_service.get_rag_response(db=db, query=query.question)
    return create_api_response(data=ChatResponseData(answer=response_text))
