from typing import Annotated

from dependencies import get_db
from fastapi import APIRouter, Depends
from modules.ai_service import ai_service
from schemas.assistant import ChatQuery, ChatResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Interact with the Business Intelligence AI Assistant",
    description="""
    Send a question in natural language to get insights about sales data.
    The assistant uses a RAG (Retrieval-Augmented Generation) pipeline
    to answer based on the information stored in the sales database.
    """,
)
async def assistant_chat(
    query: ChatQuery,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Handles a user's query by passing it to the AI service's RAG pipeline.
    """
    response_text = await ai_service.get_rag_response(db=db, query=query.query)
    return ChatResponse(response=response_text)
