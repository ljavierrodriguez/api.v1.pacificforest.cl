from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date


class OperacionExportacionCreate(BaseModel):
    referencia: Optional[str] = None
    fecha_operacion: Optional[date] = None

    model_config = ConfigDict(json_schema_extra={"examples": [{"referencia": "OE-1", "fecha_operacion": "2025-12-01"}]})


class OperacionExportacionRead(BaseModel):
    id_operacion_exportacion: int = Field(..., description="Descripción de id_operacion_exportacion")
    referencia: Optional[str] = Field(default=None, description="Descripción de referencia")
    fecha_operacion: Optional[date] = Field(default=None, description="Descripción de fecha_operacion")
    model_config = ConfigDict(from_attributes=True)


class OperacionExportacionUpdate(BaseModel):
    referencia: Optional[str] = None
    fecha_operacion: Optional[date] = None
    model_config = ConfigDict()
