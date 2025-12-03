from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class ContactoOrdenCompraCreate(BaseModel):
    id_orden_compra: int = Field(..., description="Descripción de id_orden_compra")
    id_contacto: int = Field(..., description="Descripción de id_contacto")

    model_config = ConfigDict(json_schema_extra={"examples": [{"id_orden_compra": 1, "id_contacto": 1}]})


class ContactoOrdenCompraRead(BaseModel):
    id_contacto_orden_compra: int = Field(..., description="Descripción de id_contacto_orden_compra")
    id_orden_compra: int = Field(..., description="Descripción de id_orden_compra")
    id_contacto: int = Field(..., description="Descripción de id_contacto")

    model_config = ConfigDict(from_attributes=True)


class ContactoOrdenCompraUpdate(BaseModel):
    id_orden_compra: Optional[int] = None
    id_contacto: Optional[int] = None

    model_config = ConfigDict()
