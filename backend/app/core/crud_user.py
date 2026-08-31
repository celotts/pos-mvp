from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.crud_base import CRUDBase, sanitize_pagination
from core.security import get_password_hash, verify_password
from models.role import Role
from models.user import User
from schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def __init__(self, model: type[User]):
        super().__init__(model)
        # Asegura que el rol y sus permisos se carguen eficientemente (RBAC).
        self.default_loads = [
            selectinload(self.model.role).selectinload(Role.permissions)
        ]

    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        query = select(self.model).filter(func.lower(self.model.email) == email.lower())
        if self.default_loads:
            query = query.options(*self.default_loads)

        result = await db.execute(query)
        return result.scalars().first()

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> User | None:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    async def register_failed_attempt(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        max_attempts: int,
        lock_seconds: int,
    ) -> User:
        """Incrementa los intentos fallidos y bloquea la cuenta al alcanzar el máximo."""
        db_obj.failed_login_attempts = (db_obj.failed_login_attempts or 0) + 1
        if db_obj.failed_login_attempts >= max_attempts:
            db_obj.locked_until = datetime.now(timezone.utc) + timedelta(
                seconds=lock_seconds
            )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def reset_failed_attempts(self, db: AsyncSession, *, db_obj: User) -> User:
        """Limpia los intentos fallidos tras un login correcto."""
        db_obj.failed_login_attempts = 0
        db_obj.locked_until = None
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = self.model(
            email=obj_in.email,
            full_name=obj_in.full_name,
            password=get_password_hash(obj_in.password.get_secret_value()),
            role_id=obj_in.role_id,
        )
        db.add(db_obj)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: User, obj_in: UserUpdate | dict[str, Any]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Si se proporciona una contraseña, la hasheamos.
        if password := update_data.get("password"):
            update_data["password"] = get_password_hash(password)
        # Si la contraseña está en los datos pero está vacía/nula, la eliminamos para no sobreescribir.
        elif "password" in update_data:
            del update_data["password"]

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        email: str | None = None,
    ) -> list[User]:
        skip, limit = sanitize_pagination(skip, limit)
        query = select(self.model)
        if email:
            query = query.filter(self.model.email == email)
        query = query.options(*self.default_loads)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())


crud_user = CRUDUser(User)
