from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date


class PleCreate(BaseModel):
    id_estado_pl: Optional[int] = None
    fecha: Optional[date] = None
    model_config = ConfigDict(json_schema_extra={"examples": [{"id_estado_pl": 1, "fecha": "2025-12-01"}]})


class PleRead(BaseModel):
    id_ple: int = Field(..., description="Descripción de id_ple")
    id_estado_pl: Optional[int] = Field(default=None, description="Descripción de id_estado_pl")
    fecha: Optional[date] = Field(default=None, description="Descripción de fecha")
    model_config = ConfigDict(from_attributes=True)


class PleUpdate(BaseModel):
    id_estado_pl: Optional[int] = None
    fecha: Optional[date] = None
    model_config = ConfigDict()
