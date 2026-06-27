from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """O que o cliente manda para criar conta."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """O que a API devolve — nunca inclui a senha."""
    id: int
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Resposta do login — contém o JWT."""
    access_token: str
    token_type: str = "bearer"
