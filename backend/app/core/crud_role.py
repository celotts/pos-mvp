from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.crud_base import CRUDBase
from models.role import Role
from schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def __init__(self, model: type[Role]):
        super().__init__(model)
        # RBAC: precarga permisos (serialización) y usuarios (delete-guard) sin
        # disparar lazy-load async.
        self.default_loads = [
            selectinload(self.model.permissions),
            selectinload(self.model.users),
        ]

    async def get_by_name(self, db: AsyncSession, *, name: str) -> Role | None:
        result = await db.execute(
            select(self.model)
            .options(*self.default_loads)
            .filter(self.model.name == name)
        )
        return result.scalars().first()


crud_role = CRUDRole(Role)
