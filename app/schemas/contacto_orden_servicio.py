from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class ContactoOrdenServicioCreate(BaseModel):
    id_contacto: int = Field(..., description="ID del contacto")


    model_config = ConfigDict(json_schema_extra={"examples": [{"id_contacto": 1, "id_orden_servicio": 1}]})


class ContactoOrdenServicioRead(BaseModel):
    id_contacto_orden_servicio: int
    id_contacto: int
    id_orden_servicio: int
    # Datos del contacto desnormalizados para el frontend
    contacto_nombre: Optional[str] = None
    contacto_correo: Optional[str] = None
    contacto_telefono: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ContactoOrdenServicioUpdate(BaseModel):
    id_contacto: Optional[int] = None
    id_orden_servicio: Optional[int] = None

    model_config = ConfigDict()


