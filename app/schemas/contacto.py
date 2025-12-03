from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class ContactoCreate(BaseModel):
    nombre: str = Field(..., description="Descripción de nombre")
    correo: Optional[str] = None
    telefono: Optional[str] = None
    id_cliente_proveedor: int = Field(..., description="Descripción de id_cliente_proveedor")

    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {"nombre": "Juan Perez", "correo": "juan@example.com", "telefono": "+56912345678", "id_cliente_proveedor": 1}
        ]
    })


class ContactoRead(BaseModel):
    id_contacto: int = Field(..., description="Descripción de id_contacto")
    nombre: str = Field(..., description="Descripción de nombre")
    correo: Optional[str] = None
    telefono: Optional[str] = None
    id_cliente_proveedor: int = Field(..., description="Descripción de id_cliente_proveedor")

    model_config = ConfigDict(from_attributes=True)


class ContactoUpdate(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    id_cliente_proveedor: Optional[int] = None

    model_config = ConfigDict()
