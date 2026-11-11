from typing import Any, Optional, List, Dict
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from app.schemas.seguridad import SeguridadRead


class Token(BaseModel):
    access_token: str = Field(..., description="Descripción de access_token")
    token_type: str = Field(..., description="Descripción de token_type")


class TokenWithUser(BaseModel):
    access_token: str = Field(default="", description="Token de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")
    user: Optional["UserRead"] = Field(default=None, description="Información del usuario")
    requires_2fa: bool = Field(default=False, description="Indica si se requiere verificación de segundo factor (2FA)")
    temp_token: Optional[str] = Field(default=None, description="Token temporal para completar el desafío 2FA")


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    rut: Optional[str] = Field(default="", description="RUT del usuario")
    login: str = Field(..., description="Login del usuario")
    nombre: str = Field(..., description="Nombre del usuario")
    correo: str = Field(..., description="Correo del usuario")
    telefono: Optional[str] = Field(default="", description="Teléfono del usuario")
    rol: Optional[str] = Field(default="PERSONALIZADO", description="Rol del usuario en el sistema")


class UserSeguridadInput(BaseModel):
    modulo: str = Field(..., max_length=60, description="Nombre del módulo")
    crear: bool = Field(default=False, description="Permiso para crear")
    ver: bool = Field(default=False, description="Permiso para ver")
    editar: bool = Field(default=False, description="Permiso para editar")
    eliminar: bool = Field(default=False, description="Permiso para eliminar")


class UserCreate(UserBase):
    password: str
    url_firma: Optional[str] = Field(None, description="URL de la imagen de firma del usuario")
    activo: Optional[bool] = Field(default=True, description="Indica si el usuario está activo")
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


class UserRead(UserBase):
    id_usuario: int
    activo: bool = Field(default=True, description="Indica si el usuario está activo")
    url_firma: Optional[str] = Field(None, description="URL de la imagen de firma del usuario")
    rol: str = Field(default="PERSONALIZADO", description="Rol asignado al usuario")
    two_factor_enabled: bool = Field(default=False, description="Indica si el usuario tiene 2FA activo")
    backup_codes_remaining: int = Field(default=0, description="Cantidad de códigos de respaldo 2FA disponibles")
    seguridades: List[SeguridadRead] = Field(default_factory=list, description="Lista de permisos de seguridad del usuario")

    @field_validator("rut", "telefono", mode="before")
    @classmethod
    def default_empty_str(cls, v):
        return v if v is not None else ""

    @field_validator("rol", mode="before")
    @classmethod
    def default_rol(cls, v):
        return (v or "PERSONALIZADO").strip().upper() if isinstance(v, str) else "PERSONALIZADO"

    @field_validator("nombre", mode="before")
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
        description="Permisos normalizados por módulo: {MODULO: {crear, ver, editar, eliminar, id_seguridad}}"
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
    rol: Optional[str] = Field(None, description="Rol del usuario")
    activo: Optional[bool] = None
    seguridades: Optional[List[UserSeguridadInput]] = None
    permisos: Optional[Dict[str, Dict[str, Any]]] = None
    permissions: Optional[Dict[str, Dict[str, Any]]] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., description="Correo del usuario")


class PasswordResetConfirm(BaseModel):
    token: str = Field(..., description="Token de restablecimiento")
    new_password: str = Field(..., description="Nueva contraseña")


class ProfileUpdateRequest(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=120, description="Nombre completo del usuario")
    correo: EmailStr = Field(..., description="Correo electrónico del usuario")
    telefono: Optional[str] = Field(default="", max_length=50, description="Teléfono de contacto")
    rut: Optional[str] = Field(default="", max_length=20, description="RUT del usuario")


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, description="Contraseña actual")
    new_password: str = Field(..., min_length=6, description="Nueva contraseña (mínimo 6 caracteres)")
    confirm_password: Optional[str] = Field(default=None, description="Confirmación de la nueva contraseña")


class TwoFactorSetupRequest(BaseModel):
    current_password: str = Field(..., min_length=1, description="Contraseña actual para autorizar configuración 2FA")


class TwoFactorSetupResponse(BaseModel):
    secret: str = Field(..., description="Secreto Base32 para ingreso manual")
    otpauth_uri: str = Field(..., description="URI otpauth://totp/...")
    qr_code: str = Field(..., description="Data URI SVG en base64 del código QR")
    issuer: str = Field(..., description="Nombre del emisor")
    account: str = Field(..., description="Cuenta asociada")


class TwoFactorVerifyRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=20, description="Código de 6 dígitos de la app autenticadora")


class TwoFactorEnableResponse(BaseModel):
    enabled: bool = Field(..., description="Estado de activación de 2FA")
    backup_codes: List[str] = Field(default_factory=list, description="Códigos de respaldo de un solo uso")
    user: UserRead = Field(..., description="Usuario actualizado")


class TwoFactorDisableRequest(BaseModel):
    current_password: str = Field(..., min_length=1, description="Contraseña actual")
    code: Optional[str] = Field(default=None, description="Código 2FA o código de respaldo")


class TwoFactorLoginRequest(BaseModel):
    temp_token: str = Field(..., description="Token temporal emitido tras validar usuario y contraseña")
    code: str = Field(..., min_length=6, max_length=20, description="Código TOTP de 6 dígitos o código de respaldo")


UserBase.model_rebuild()
UserRead.model_rebuild()
UserUpdate.model_rebuild()
TokenWithUser.model_rebuild()
TwoFactorEnableResponse.model_rebuild()
