import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.crud_base import CRUDBase
from core.tenancy import get_current_tenant
from models.shift import Shift, ShiftStatus
from schemas.shift import ShiftClose as ShiftUpdate
from schemas.shift import ShiftOpen as ShiftCreate


class CRUDShift(CRUDBase[Shift, ShiftCreate, ShiftUpdate]):
    def __init__(self, model: type[Shift]):
        super().__init__(model)
        self.default_loads = [
            selectinload(self.model.user),
            selectinload(self.model.pos_terminal),
        ]

    async def get_open_shift_by_terminal(
        self, db: AsyncSession, *, terminal_id: uuid.UUID
    ) -> Shift | None:
        stmt = select(self.model).filter_by(
            pos_terminal_id=terminal_id, status=ShiftStatus.OPEN
        )
        tenant_id = get_current_tenant()
        if tenant_id:
            stmt = stmt.where(self.model.tenant_id == tenant_id)
        result = await db.execute(stmt)
        return result.scalars().first()


crud_shift = CRUDShift(Shift)
