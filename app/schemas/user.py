
from typing import Optional, List, Dict
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from app.schemas.seguridad import SeguridadRead


class Token(BaseModel):
    access_token: str = Field(..., description="Descripción de access_token")
    token_type: str = Field(..., description="Descripción de token_type")
    


class TokenWithUser(BaseModel):
    access_token: str = Field(..., description="Token de acceso")
    token_type: str = Field(..., description="Tipo de token")
    user: "UserRead" = Field(..., description="Información del usuario")
 


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    login: str = Field(..., description="Descripción de login")
    nombre: str = Field(..., description="Descripción de nombre")
    correo: EmailStr = Field(..., description="Descripción de correo")


class UserCreate(UserBase):
    password: str
    url_firma: Optional[str] = Field(None, description="URL de la imagen de firma del usuario")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "login": "johndoe_new",
                    "nombre": "John Doe",
                    "correo": "johndoe_new@example.com",
                    "password": "newstrongpassword",
                    "url_firma": "https://example.com/firmas/johndoe.png"
                }
            ]
        }
    )


class UserRead(UserBase):
    id_usuario: int
    url_firma: Optional[str] = Field(None, description="URL de la imagen de firma del usuario")
    seguridades: List[SeguridadRead] = Field(default_factory=list, description="Lista de permisos de seguridad del usuario")

    @field_validator('nombre', mode='before')
    @classmethod
    def capitalize_nombre(cls, v):
        """Capitaliza la primera letra de cada palabra en el nombre"""
        if isinstance(v, str):
            return v.title()
        return v
    
    permissions: Dict[str, Dict[str, bool]] = Field(
        default_factory=dict,
        description="Permisos normalizados por módulo: {MODULO: {create, read, update, delete}}"
    )
    
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    login: Optional[str] = None
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    password: Optional[str] = None
    telefono: Optional[str] = None
    url_firma: Optional[str] = Field(None, description="URL de la imagen de firma del usuario")
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
                    "url_firma": "https://example.com/firmas/johndoe_updated.png",
                    "activo": True,
                }
            ]
        }
    )



UserBase.model_rebuild()
UserRead.model_rebuild()
UserUpdate.model_rebuild()
TokenWithUser.model_rebuild()
