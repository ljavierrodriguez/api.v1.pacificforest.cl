from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class MonedaCreate(BaseModel):
    id_moneda: Optional[int] = None
    etiqueta: str = Field(..., description="Descripción de etiqueta")
    nombre_moneda: Optional[str] = None
    por_defecto: Optional[bool] = False

    model_config = ConfigDict(json_schema_extra={"examples": [{"id_moneda": 1, "etiqueta": "USD", "nombre_moneda": "Dólar", "por_defecto": True}]})


class MonedaRead(BaseModel):
    id_moneda: int = Field(..., description="Descripción de id_moneda")
    etiqueta: str = Field(..., description="Descripción de etiqueta")
    nombre_moneda: Optional[str] = Field(default=None, description="Descripción de nombre_moneda")
    por_defecto: bool = Field(..., description="Descripción de por_defecto")

    model_config = ConfigDict(from_attributes=True)


class MonedaUpdate(BaseModel):
    etiqueta: Optional[str] = None
    nombre_moneda: Optional[str] = None
    por_defecto: Optional[bool] = None
    model_config = ConfigDict()
