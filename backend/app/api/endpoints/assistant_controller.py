# api/endpoints/assistant_controller.py
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from httpx import HTTPError
from langchain_core.exceptions import OutputParserException
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps_auth import require_permission
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_db
from models.user import User as UserModel
from schemas.assistant import ChatRequest, ChatResponse
from service.ai_agent_service import ai_agent_service
from service.ai_service import ai_service
from utils.logger import logger

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])

# Inyección de dependencias reutilizable
db_dependency = Depends(get_db)
current_user_dependency = Depends(require_permission("assistant:use"))


@router.post(
    "/analyze-inventory-flow",
    response_model=ApiResponse[ChatResponse],
    summary="Analyze Inventory Flow with ReAct Agent",
    status_code=status.HTTP_200_OK,
)
async def analyze_inventory_flow(
    query: ChatRequest,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """
    Analiza el flujo de inventario y responde consultas utilizando el agente ReAct.
    """
    try:
        response_text = await ai_service.get_purchase_suggestion(
            db=db, query=query.message, store_id=query.context_store_id
        )
        return create_api_response(data=ChatResponse(answer=response_text))
    except (OutputParserException, HTTPError, ValueError) as exc:
        logger.error(f"Error de ejecución en el agente de IA: {exc!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la solicitud con el agente: {exc!s}",
        )
    except KeyError as exc:
        logger.error(f"Clave faltante en la respuesta del LLM: {exc!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Respuesta malformada del servicio de IA: falta la clave {exc!s}",
        )


@router.post(
    "/chat",
    response_model=ApiResponse[ChatResponse],
    summary="Toma de decisiones asistida por IA",
    status_code=status.HTTP_200_OK,
)
async def ask_assistant(
    request: ChatRequest,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """
    Endpoint principal para la toma de decisiones ejecutivas y estratégicas asistida por IA.
    """
    try:
        result = await ai_agent_service.process_decision_request(db=db, request=request)
        return create_api_response(data=result)
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Error procesando la toma de decisiones: {exc!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno en el módulo de decisiones: {exc!s}",
        )
