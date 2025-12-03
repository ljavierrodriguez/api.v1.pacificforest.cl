from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class TipoEnvaseCreate(BaseModel):
    nombre: str = Field(..., description="Descripción de nombre")

    model_config = ConfigDict(json_schema_extra={"examples": [{"nombre": "CAJA"}]})


class TipoEnvaseRead(BaseModel):
    id_tipo_envase: int = Field(..., description="Descripción de id_tipo_envase")
    nombre: str = Field(..., description="Descripción de nombre")

    model_config = ConfigDict(from_attributes=True)


class TipoEnvaseUpdate(BaseModel):
    nombre: Optional[str] = None
    model_config = ConfigDict()
