import uuid

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_db
from fastapi import APIRouter, Depends, status
from models.user import User as UserModel
from modules import country_service
from schemas.country import Country, CountryCreate, CountryUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Countries"])

db_dependency = Depends(get_db)
admin_user_dependency = Depends(get_current_admin_user)


@router.post(
    "/", response_model=ApiResponse[Country], status_code=status.HTTP_201_CREATED
)
async def create_country(
    *,
    country_in: CountryCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = admin_user_dependency,
) -> ApiResponse[Country]:
    """Create a new country. For administrators only."""
    new_country = await country_service.create_country(
        db=db,
        country_in=country_in,
        user_id=current_user.id,
    )
    return create_api_response(
        data=new_country,
        status_code=status.HTTP_201_CREATED,
        message="Country created successfully.",
    )


@router.get("/", response_model=ApiResponse[list[Country]])
async def read_countries(
    db: AsyncSession = db_dependency, skip: int = 0, limit: int = 100
) -> ApiResponse[list[Country]]:
    """Get a list of countries."""
    all_countries = await country_service.get_countries(db, skip=skip, limit=limit)
    return create_api_response(data=all_countries)


@router.get("/{country_id}", response_model=ApiResponse[Country])
async def read_country(
    *, country_id: uuid.UUID, db: AsyncSession = db_dependency
) -> ApiResponse[Country]:
    """Get a country by its ID."""
    return create_api_response(
        data=await country_service.get_country(db, country_id=country_id)
    )


@router.put("/{country_id}", response_model=ApiResponse[Country])
async def update_country(
    *,
    country_id: uuid.UUID,
    country_in: CountryUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = admin_user_dependency,
) -> ApiResponse[Country]:
    """Update a country. For administrators only."""
    updated_country = await country_service.update_country(
        db=db, country_id=country_id, country_in=country_in, user_id=current_user.id
    )
    return create_api_response(
        data=updated_country, message="Country updated successfully."
    )


@router.delete("/{country_id}", response_model=ApiResponse[Country])
async def delete_country(
    *,
    country_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = admin_user_dependency,
) -> ApiResponse[Country]:
    """Delete a country. For administrators only."""
    deleted_country = await country_service.remove_country(db=db, country_id=country_id)
    return create_api_response(
        data=deleted_country, message="Country deleted successfully."
    )
