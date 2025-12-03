from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class ContenedorCreate(BaseModel):
    nombre: str = Field(..., description="Descripción de nombre")
    tara: Optional[float] = None
    peso_maximo: Optional[float] = None

    model_config = ConfigDict(json_schema_extra={"examples": [{"nombre":"CONT-20","tara":2.5,"peso_maximo":2500.0}]})


class ContenedorRead(BaseModel):
    id_contenedor: int = Field(..., description="Descripción de id_contenedor")
    nombre: str = Field(..., description="Descripción de nombre")
    tara: Optional[float] = None
    peso_maximo: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ContenedorUpdate(BaseModel):
    nombre: Optional[str] = None
    tara: Optional[float] = None
    peso_maximo: Optional[float] = None

    model_config = ConfigDict()
