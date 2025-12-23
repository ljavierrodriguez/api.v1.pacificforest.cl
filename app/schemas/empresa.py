from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class EmpresaCreate(BaseModel):
    rut: str = Field(..., description="RUT de la empresa")
    nombre_fantasia: str = Field(..., description="Nombre de fantasía de la empresa")
    razon_social: str = Field(..., description="Razón social de la empresa")
    direccion: str = Field(..., description="Dirección de la empresa")
    telefono_1: Optional[str] = Field(default=None, description="Teléfono principal")
    telefono_2: Optional[str] = Field(default=None, description="Teléfono secundario")
    giro: Optional[str] = Field(default=None, description="Giro comercial de la empresa")
    id_ciudad: int = Field(..., description="ID de la ciudad")
    es_vigente: Optional[bool] = Field(default=True, description="Indica si la empresa está vigente")
    en_proforma: Optional[bool] = Field(default=False, description="Indica si aparece en proformas")
    en_odc: Optional[bool] = Field(default=False, description="Indica si aparece en órdenes de compra")
    por_defecto: Optional[bool] = Field(default=False, description="Indica si es la empresa por defecto")
    url_logo: str = Field(..., description="URL del logo de la empresa")

    model_config = ConfigDict(json_schema_extra={
        "examples": [{
            "rut": "12.345.678-9",
            "nombre_fantasia": "Empresa Demo",
            "razon_social": "Empresa Demo S.A.",
            "direccion": "Av. Principal 123",
            "telefono_1": "+56912345678",
            "giro": "Comercio al por mayor",
            "id_ciudad": 1,
            "url_logo": "https://example.com/logo.png"
        }]
    })


class EmpresaRead(BaseModel):
    id_empresa: int = Field(..., description="ID único de la empresa")
    rut: Optional[str] = Field(default=None, description="RUT de la empresa")
    nombre_fantasia: str = Field(..., description="Nombre de fantasía de la empresa")
    razon_social: str = Field(..., description="Razón social de la empresa")
    direccion: str = Field(..., description="Dirección de la empresa")
    telefono_1: Optional[str] = Field(default=None, description="Teléfono principal")
    telefono_2: Optional[str] = Field(default=None, description="Teléfono secundario")
    giro: Optional[str] = Field(default=None, description="Giro comercial de la empresa")
    id_ciudad: int = Field(..., description="ID de la ciudad")
    es_vigente: bool = Field(..., description="Indica si la empresa está vigente")
    en_proforma: bool = Field(..., description="Indica si aparece en proformas")
    en_odc: bool = Field(..., description="Indica si aparece en órdenes de compra")
    por_defecto: bool = Field(..., description="Indica si es la empresa por defecto")
    url_logo: str = Field(..., description="URL del logo de la empresa")

    model_config = ConfigDict(from_attributes=True)


class EmpresaUpdate(BaseModel):
    rut: Optional[str] = Field(default=None, description="RUT de la empresa")
    nombre_fantasia: Optional[str] = Field(default=None, description="Nombre de fantasía de la empresa")
    razon_social: Optional[str] = Field(default=None, description="Razón social de la empresa")
    direccion: Optional[str] = Field(default=None, description="Dirección de la empresa")
    telefono_1: Optional[str] = Field(default=None, description="Teléfono principal")
    telefono_2: Optional[str] = Field(default=None, description="Teléfono secundario")
    giro: Optional[str] = Field(default=None, description="Giro comercial de la empresa")
    id_ciudad: Optional[int] = Field(default=None, description="ID de la ciudad")
    es_vigente: Optional[bool] = Field(default=None, description="Indica si la empresa está vigente")
    en_proforma: Optional[bool] = Field(default=None, description="Indica si aparece en proformas")
    en_odc: Optional[bool] = Field(default=None, description="Indica si aparece en órdenes de compra")
    por_defecto: Optional[bool] = Field(default=None, description="Indica si es la empresa por defecto")
    url_logo: Optional[str] = Field(default=None, description="URL del logo de la empresa")
    
    model_config = ConfigDict()
