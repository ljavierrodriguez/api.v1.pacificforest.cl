from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date


class ProformaCreate(BaseModel):
    id_cliente_proveedor: Optional[int] = None
    fecha: Optional[date] = None
    total: Optional[str] = None
    model_config = ConfigDict(json_schema_extra={"examples": [{"id_cliente_proveedor": 1, "fecha": "2025-12-01", "total": "1000"}]})


class ProformaRead(BaseModel):
    id_proforma: int = Field(..., description="Descripción de id_proforma")
    id_cliente_proveedor: Optional[int] = Field(default=None, description="Descripción de id_cliente_proveedor")
    fecha: Optional[date] = Field(default=None, description="Descripción de fecha")
    total: Optional[str] = Field(default=None, description="Descripción de total")
    model_config = ConfigDict(from_attributes=True)


class ProformaUpdate(BaseModel):
    total: Optional[str] = None
    model_config = ConfigDict()
