from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class BodegaCreate(BaseModel):
    nombre: str = Field(..., description="Nombre de la bodega", max_length=200)
    direccion: Optional[str] = Field(None, description="Dirección de la bodega", max_length=200)

    model_config = ConfigDict(json_schema_extra={"examples": [{"nombre": "Bodega Central", "direccion": "Av. Principal 123"}]})


class BodegaRead(BaseModel):
    id_bodega: int = Field(..., description="ID único de la bodega")
    nombre: str = Field(..., description="Nombre de la bodega")
    direccion: Optional[str] = Field(None, description="Dirección de la bodega")

    model_config = ConfigDict(from_attributes=True)


class BodegaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    direccion: Optional[str] = Field(None, max_length=200)
    
    model_config = ConfigDict()