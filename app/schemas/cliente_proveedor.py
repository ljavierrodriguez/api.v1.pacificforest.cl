from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

from app.schemas.ciudad import CiudadRead
from app.schemas.contacto import ContactoRead
from app.schemas.direccion import DireccionRead
from app.schemas.pais import PaisRead


class ClienteProveedorCreate(BaseModel):
    rut: Optional[str] = None
    nombre_fantasia: str = Field(..., description="Descripción de nombre_fantasia")
    razon_social: str = Field(..., description="Descripción de razon_social")
    es_nacional: bool = Field(..., description="Descripción de es_nacional")
    giro: Optional[str] = None
    es_cliente: bool = Field(..., description="Descripción de es_cliente")
    es_proveedor: bool = Field(..., description="Descripción de es_proveedor")

    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "rut": "12.345.678-9",
                "nombre_fantasia": "Empresa Ejemplo",
                "razon_social": "Empresa Ejemplo S.A.",
                "es_nacional": True,
                "giro": "Exportación",
                "es_cliente": True,
                "es_proveedor": False,
            }
        ]
    })


class ClienteProveedorRead(BaseModel):
    id_cliente_proveedor: int = Field(..., description="Descripción de id_cliente_proveedor")
    rut: Optional[str] = None
    nombre_fantasia: str = Field(..., description="Descripción de nombre_fantasia")
    razon_social: str = Field(..., description="Descripción de razon_social")
    es_nacional: bool = Field(..., description="Descripción de es_nacional")
    giro: Optional[str] = None
    es_cliente: bool = Field(..., description="Descripción de es_cliente")
    es_proveedor: bool = Field(..., description="Descripción de es_proveedor")

    model_config = ConfigDict(from_attributes=True)


class CiudadDetalleRead(CiudadRead):
    Pais: Optional[PaisRead] = None

    model_config = ConfigDict(from_attributes=True)


class DireccionDetalleRead(DireccionRead):
    Ciudad: Optional[CiudadDetalleRead] = None

    model_config = ConfigDict(from_attributes=True)


class ClienteProveedorDetailRead(ClienteProveedorRead):
    Contactos: list[ContactoRead] = Field(default_factory=list)
    Direcciones: list[DireccionDetalleRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ClienteProveedorUpdate(BaseModel):
    rut: Optional[str] = None
    nombre_fantasia: Optional[str] = None
    razon_social: Optional[str] = None
    es_nacional: Optional[bool] = None
    giro: Optional[str] = None
    es_cliente: Optional[bool] = None
    es_proveedor: Optional[bool] = None

    model_config = ConfigDict()
