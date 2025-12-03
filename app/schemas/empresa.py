from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional


class EmpresaCreate(BaseModel):
    rut: Optional[str] = None
    razon_social: str = Field(..., description="Descripción de razon_social")
    nombre_fantasia: Optional[str] = None
    correo: Optional[EmailStr] = None

    model_config = ConfigDict(json_schema_extra={"examples": [{"rut": "12.345.678-9", "razon_social": "Empresa S.A."}]})


class EmpresaRead(BaseModel):
    id_empresa: int = Field(..., description="Descripción de id_empresa")
    rut: Optional[str] = Field(default=None, description="Descripción de rut")
    razon_social: str = Field(..., description="Descripción de razon_social")
    nombre_fantasia: Optional[str] = Field(default=None, description="Descripción de nombre_fantasia")
    correo: Optional[EmailStr] = Field(default=None, description="Descripción de correo")

    model_config = ConfigDict(from_attributes=True)


class EmpresaUpdate(BaseModel):
    razon_social: Optional[str] = None
    nombre_fantasia: Optional[str] = None
    correo: Optional[EmailStr] = None
    model_config = ConfigDict()
