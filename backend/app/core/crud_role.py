from core.crud_base import CRUDBase
from models.role import Role
from schemas.role import RoleCreate, RoleUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Role | None:
        result = await db.execute(select(self.model).filter(self.model.name == name))
        return result.scalars().first()


crud_role = CRUDRole(Role)
