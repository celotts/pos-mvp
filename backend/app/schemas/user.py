import uuid

from pydantic import BaseModel, EmailStr, SecretStr


class UserBase(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None


class UserBootstrapIn(UserBase):
    """Esquema para la entrada del endpoint de bootstrap."""

    email: EmailStr
    password: SecretStr
    full_name: str


class UserLogin(BaseModel):
    """Esquema para el login de usuario."""

    email: EmailStr
    password: SecretStr


class UserCreate(UserBootstrapIn):
    """Esquema para crear un usuario con un rol específico."""

    role_id: uuid.UUID


class UserUpdate(UserBase):
    password: str | None = None


class UserInDBBase(UserBase):
    id: uuid.UUID
    email: EmailStr
    full_name: str

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass
