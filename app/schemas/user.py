from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class Token(BaseModel):
    access_token: str = Field(..., description="Descripción de access_token")
    token_type: str = Field(..., description="Descripción de token_type")


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    login: str = Field(..., description="Descripción de login")
    nombre: str = Field(..., description="Descripción de nombre")
    correo: EmailStr = Field(..., description="Descripción de correo")


class UserCreate(UserBase):
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "login": "johndoe_new",
                    "nombre": "John Doe",
                    "correo": "johndoe_new@example.com",
                    "password": "newstrongpassword"
                }
            ]
        }
    )


class UserRead(UserBase):
    id_usuario: int

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    login: Optional[str] = None
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    password: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "login": "johndoe",
                    "nombre": "John Doe Updated",
                    "correo": "johndoe_updated@example.com",
                    "password": "newpassword123",
                    "telefono": "+56912345678",
                    "activo": True,
                }
            ]
        }
    )
