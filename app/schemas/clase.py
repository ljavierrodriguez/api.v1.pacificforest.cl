from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class ClaseCreate(BaseModel):
    nombre: str = Field(..., description="Descripción de nombre")
    model_config = ConfigDict(json_schema_extra={"examples": [{"nombre": "Clase A"}]})


class ClaseRead(BaseModel):
    id_clase: int = Field(..., description="Descripción de id_clase")
    nombre: str = Field(..., description="Descripción de nombre")
    model_config = ConfigDict(from_attributes=True)


class ClaseUpdate(BaseModel):
    nombre: Optional[str] = None
    model_config = ConfigDict()
