from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class EstadoPlCreate(BaseModel):
    nombre: str = Field(..., description="Descripción de nombre")
    es_ple: Optional[bool] = False
    es_plc: Optional[bool] = False

    model_config = ConfigDict(json_schema_extra={"examples": [{"nombre": "Creado", "es_ple": False, "es_plc": True}]})


class EstadoPlRead(BaseModel):
    id_estado_pl: int = Field(..., description="Descripción de id_estado_pl")
    nombre: str = Field(..., description="Descripción de nombre")
    es_ple: bool = Field(..., description="Descripción de es_ple")
    es_plc: bool = Field(..., description="Descripción de es_plc")

    model_config = ConfigDict(from_attributes=True)


class EstadoPlUpdate(BaseModel):
    nombre: Optional[str] = None
    es_ple: Optional[bool] = None
    es_plc: Optional[bool] = None

    model_config = ConfigDict()
