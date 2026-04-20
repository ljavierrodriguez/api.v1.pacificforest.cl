
from typing import Any, Optional, List, Dict
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
    rut: str = Field(..., description="RUT del usuario")
    login: str = Field(..., description="Descripción de login")
    nombre: str = Field(..., description="Descripción de nombre")
    correo: EmailStr = Field(..., description="Descripción de correo")
    telefono: str = Field(..., description="Teléfono del usuario")


class UserSeguridadInput(BaseModel):
    modulo: str = Field(..., max_length=15, description="Nombre del módulo")
    crear: bool = Field(default=False, description="Permiso para crear")
    ver: bool = Field(default=False, description="Permiso para ver")
    editar: bool = Field(default=False, description="Permiso para editar")
    eliminar: bool = Field(default=False, description="Permiso para eliminar")


class UserCreate(UserBase):
    password: str
    url_firma: Optional[str] = Field(None, description="URL de la imagen de firma del usuario")
    seguridades: List[UserSeguridadInput] = Field(
        default_factory=list,
        description="Permisos iniciales del usuario por módulo, con valores true/false"
    )
    permisos: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Compatibilidad: permisos por módulo con claves en español"
    )
    permissions: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Permisos por módulo con claves en inglés"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "rut": "12345678-9",
                    "login": "johndoe_new",
                    "nombre": "John Doe",
                    "correo": "johndoe_new@example.com",
                    "telefono": "+56912345678",
                    "password": "newstrongpassword",
                    "url_firma": "https://example.com/firmas/johndoe.png",
                    "seguridades": [
                        {
                            "modulo": "proforma",
                            "crear": True,
                            "ver": True,
                            "editar": False,
                            "eliminar": False
                        },
                        {
                            "modulo": "usuario",
                            "crear": False,
                            "ver": True,
                            "editar": False,
                            "eliminar": False
                        }
                    ]
                }
            ]
        }
    )


class UserRead(UserBase):
    id_usuario: int
    activo: bool = Field(default=True, description="Indica si el usuario está activo")
    url_firma: Optional[str] = Field(None, description="URL de la imagen de firma del usuario")
    seguridades: List[SeguridadRead] = Field(default_factory=list, description="Lista de permisos de seguridad del usuario")

    @field_validator('nombre', mode='before')
    @classmethod
    def capitalize_nombre(cls, v):
        """Capitaliza la primera letra de cada palabra en el nombre"""
        if isinstance(v, str):
            return v.title()
        return v

    permisos: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Compatibilidad: permisos por módulo con claves en español {MODULO: {crear, ver, editar, eliminar, id_seguridad}}"
    )

    permissions: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Permisos normalizados por módulo: {MODULO: {create, read, update, delete, id_seguridad}}"
    )

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    rut: Optional[str] = None
    login: Optional[str] = None
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    password: Optional[str] = None
    telefono: Optional[str] = None
    url_firma: Optional[str] = Field(None, description="URL de la imagen de firma del usuario")
    activo: Optional[bool] = None
    seguridades: Optional[List[UserSeguridadInput]] = None
    permisos: Optional[Dict[str, Dict[str, Any]]] = None
    permissions: Optional[Dict[str, Dict[str, Any]]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "rut": "12345678-9",
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


class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., description="Correo del usuario")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "johndoe@example.com"
                }
            ]
        }
    )

class PasswordResetConfirm(BaseModel):
    token: str = Field(..., description="Token de restablecimiento")
    new_password: str = Field(..., description="Nueva contraseña")



UserBase.model_rebuild()
UserRead.model_rebuild()
UserUpdate.model_rebuild()
TokenWithUser.model_rebuild()
