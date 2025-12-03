from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class UnidadVentaCreate(BaseModel):
    nombre: str = Field(..., description="Descripción de nombre")
    cubicacion: str = Field(..., description="Descripción de cubicacion")
    descripcion: str = Field(..., description="Descripción de descripcion")
    por_defecto: Optional[bool] = False

    model_config = ConfigDict(json_schema_extra={"examples": [{"nombre": "Metro", "cubicacion": "1.0", "descripcion": "Unidad base"}]})


class UnidadVentaRead(BaseModel):
    id_unidad_venta: int = Field(..., description="Descripción de id_unidad_venta")
    nombre: str = Field(..., description="Descripción de nombre")
    cubicacion: str = Field(..., description="Descripción de cubicacion")
    descripcion: str = Field(..., description="Descripción de descripcion")
    por_defecto: bool = Field(..., description="Descripción de por_defecto")

    model_config = ConfigDict(from_attributes=True)


class UnidadVentaUpdate(BaseModel):
    nombre: Optional[str] = None
    cubicacion: Optional[str] = None
    descripcion: Optional[str] = None
    por_defecto: Optional[bool] = None
    model_config = ConfigDict()
