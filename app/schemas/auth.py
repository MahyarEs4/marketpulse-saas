from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict

class UserRegister(BaseModel):
    tenant_slug: str
    email: EmailStr
    password: str
    full_name: str | None = None

class UserLogin(BaseModel):
    tenant_slug: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    email: EmailStr
    full_name: str | None
    is_active: bool

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str
