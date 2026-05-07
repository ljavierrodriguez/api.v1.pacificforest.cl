from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class EstadoOrdenServicioCreate(BaseModel):
    nombre: str = Field(..., max_length=20)


class EstadoOrdenServicioRead(BaseModel):
    id_estado_orden_servicio: int
    nombre: str

    model_config = ConfigDict(from_attributes=True)


class EstadoOrdenServicioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=20)

    model_config = ConfigDict()
