from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class ProductoCreate(BaseModel):
    id_clase: Optional[int] = None
    id_especie: Optional[int] = None
    nombre_producto_esp: str = Field(..., description="Descripción de nombre_producto_esp")
    nombre_producto_ing: str = Field(..., description="Descripción de nombre_producto_ing")
    obs_calidad: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={"examples": [{
        "nombre_producto_esp": "Madera A",
        "nombre_producto_ing": "Wood A",
        "obs_calidad": "Sin observaciones"
    }]})


class ProductoRead(BaseModel):
    id_producto: int = Field(..., description="Descripción de id_producto")
    id_clase: Optional[int] = Field(default=None, description="Descripción de id_clase")
    id_especie: Optional[int] = Field(default=None, description="Descripción de id_especie")
    nombre_producto_esp: str = Field(..., description="Descripción de nombre_producto_esp")
    nombre_producto_ing: str = Field(..., description="Descripción de nombre_producto_ing")

    model_config = ConfigDict(from_attributes=True)


class ProductoUpdate(BaseModel):
    nombre_producto_esp: Optional[str] = None
    nombre_producto_ing: Optional[str] = None
    obs_calidad: Optional[str] = None
    model_config = ConfigDict()
