from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.crud_user import crud_user
from core.db import get_db
from core.security import decode_access_token
from core.tenancy import set_current_tenant
from models.user import User
from service.inventory_analisis_service import InventoryAnalysisService
from service.llm_service import (
    AbstractLLMService,
    llm_service_factory,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/swagger")


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user account is inactive.",
        )
    # Propaga el tenant del usuario al request en curso (scoping de datos).
    set_current_tenant(user.tenant_id)
    return user


@lru_cache
def get_llm_service() -> AbstractLLMService:
    """
    Dependencia de FastAPI que proporciona una instancia del servicio LLM.
    Utiliza `llm_service_factory` para instanciar el proveedor configurado en
    `settings.LLM_PROVIDER` (ollama por defecto, anthropic alternativo).
    `lru_cache` asegura que el factory solo se ejecute una vez (singleton).
    """
    return llm_service_factory()


LLMServiceDep = Annotated[AbstractLLMService, Depends(get_llm_service)]


def get_inventory_analysis_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    llm_service: LLMServiceDep,
) -> InventoryAnalysisService:
    """Construye el servicio de análisis con DB y LLM ya resueltos."""
    return InventoryAnalysisService(llm_service=llm_service, db=db)


InventoryAnalysisServiceDep = Annotated[
    InventoryAnalysisService, Depends(get_inventory_analysis_service)
]
