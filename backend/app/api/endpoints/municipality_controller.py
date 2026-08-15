import uuid
from typing import Any

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, status
from models.user import User as UserModel
from modules import municipality_service
from schemas.municipality import (
    Municipality,
    MunicipalityCreate,
    MunicipalityUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Municipalities"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
current_admin_user_dependency = Depends(get_current_admin_user)


@router.post(
    "/",
    response_model=ApiResponse[Municipality],
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo Municipio",
)
async def create_municipality(
    *,
    municipality_in: MunicipalityCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Crea un nuevo municipio, asociado a un estado/provincia."""
    municipality = await municipality_service.create_municipality(
        db=db, municipality_in=municipality_in, current_user=current_user
    )
    return create_api_response(
        data=municipality,
        status_code=status.HTTP_201_CREATED,
        message="Municipio creado con éxito.",
    )


@router.get(
    "/",
    response_model=ApiResponse[list[Municipality]],
    summary="Obtener una lista de Municipios",
)
async def read_municipalities(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Obtiene una lista paginada de municipios."""
    municipalities = await municipality_service.get_municipalities(
        db, skip=skip, limit=limit
    )
    return create_api_response(data=municipalities)


@router.get(
    "/{municipality_id}",
    response_model=ApiResponse[Municipality],
    summary="Obtener un Municipio por ID",
)
async def read_municipality(
    *,
    municipality_id: uuid.UUID,
    db: AsyncSession = db_dependency,
) -> Any:
    """Obtiene un municipio específico por su ID."""
    municipality = await municipality_service.get_municipality(
        db, municipality_id=municipality_id
    )
    return create_api_response(data=municipality)


@router.put(
    "/{municipality_id}",
    response_model=ApiResponse[Municipality],
    summary="Actualizar un Municipio",
)
async def update_municipality(
    *,
    municipality_id: uuid.UUID,
    municipality_in: MunicipalityUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Actualiza un municipio por su ID."""
    updated_municipality = await municipality_service.update_municipality(
        db=db,
        municipality_id=municipality_id,
        municipality_in=municipality_in,
        current_user=current_user,
    )
    return create_api_response(
        data=updated_municipality, message="Municipio actualizado con éxito."
    )


@router.delete(
    "/{municipality_id}",
    response_model=ApiResponse[Municipality],
    summary="Eliminar un Municipio",
)
async def delete_municipality(
    *,
    municipality_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Elimina un municipio por su ID."""
    deleted_municipality = await municipality_service.remove_municipality(
        db, municipality_id=municipality_id
    )
    return create_api_response(
        data=deleted_municipality, message="Municipio eliminado con éxito."
    )
