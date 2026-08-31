from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.crud_base import CRUDBase
from models.permission import Permission
from schemas.permission import Permission as PermissionSchema


class CRUDPermission(CRUDBase[Permission, PermissionSchema, PermissionSchema]):
    async def get_by_code(self, db: AsyncSession, *, code: str) -> Permission | None:
        result = await db.execute(select(self.model).filter(self.model.code == code))
        return result.scalars().first()

    async def get_all(self, db: AsyncSession) -> list[Permission]:
        result = await db.execute(select(self.model).order_by(self.model.module))
        return list(result.scalars().all())


crud_permission = CRUDPermission(Permission)
