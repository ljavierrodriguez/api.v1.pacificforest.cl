from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class ClaseCreate(BaseModel):
    nombre: str = Field(..., description="Nombre de la clase")
    descripcion: Optional[str] = Field(None, description="Descripción de la clase")
    model_config = ConfigDict(json_schema_extra={"examples": [{"nombre": "Clase A", "descripcion": "Descripción de la clase A"}]})


class ClaseRead(BaseModel):
    id_clase: int = Field(..., description="ID único de la clase")
    nombre: str = Field(..., description="Nombre de la clase")
    descripcion: Optional[str] = Field(None, description="Descripción de la clase")
    model_config = ConfigDict(from_attributes=True)


class ClaseUpdate(BaseModel):
    nombre: Optional[str] = Field(None, description="Nombre de la clase")
    descripcion: Optional[str] = Field(None, description="Descripción de la clase")
    model_config = ConfigDict()
