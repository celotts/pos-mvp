import traceback
from typing import Any

from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, HTTPException
from httpx import HTTPError
from langchain_core.exceptions import OutputParserException
from models.user import User as UserModel
from schemas.assistant import ChatQuery, ChatResponseData
from service.ai_agent_service import agent_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)


@router.post(
    "/analyze-inventory-flow",
    response_model=ApiResponse[ChatResponseData],
    summary="Analyze Inventory Flow with ReAct Agent",
)
async def analyze_inventory_flow(
    query: ChatQuery,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    try:
        response_text = await agent_service.run(query.question)
        return create_api_response(data=ChatResponseData(answer=response_text))
    except (OutputParserException, HTTPError, ValueError) as exc:
        print("=== EXECUTION ERROR IN AGENT ===")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la solicitud con el agente: {exc!s}",
        )
    except KeyError as exc:
        print("=== MISSING KEY IN AGENT RESPONSE ===")
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail=f"Respuesta malformada del servicio de IA: falta la clave {exc!s}",
        )
