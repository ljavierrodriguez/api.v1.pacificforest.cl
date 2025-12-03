from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class CiudadCreate(BaseModel):
    nombre: str = Field(..., description="Descripción de nombre")
    id_pais: Optional[int] = None
    model_config = ConfigDict(json_schema_extra={"examples": [{"nombre": "Santiago", "id_pais": 1}]})


class CiudadRead(BaseModel):
    id_ciudad: int = Field(..., description="Descripción de id_ciudad")
    nombre: str = Field(..., description="Descripción de nombre")
    id_pais: Optional[int] = Field(default=None, description="Descripción de id_pais")
    model_config = ConfigDict(from_attributes=True)


class CiudadUpdate(BaseModel):
    nombre: Optional[str] = None
    id_pais: Optional[int] = None
    model_config = ConfigDict()
