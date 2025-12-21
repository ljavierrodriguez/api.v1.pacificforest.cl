from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class TipoComisionCreate(BaseModel):
    nombre: str = Field(..., description="Nombre del tipo de comisión", max_length=20)
    por_defecto: Optional[bool] = False

    model_config = ConfigDict(json_schema_extra={"examples": [{"nombre": "Porcentual", "por_defecto": True}]})


class TipoComisionRead(BaseModel):
    id_tipo_comision: int = Field(..., description="ID único del tipo de comisión")
    nombre: str = Field(..., description="Nombre del tipo de comisión")
    por_defecto: bool = Field(..., description="Indica si es el tipo de comisión por defecto")

    model_config = ConfigDict(from_attributes=True)


class TipoComisionUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=20)
    por_defecto: Optional[bool] = None
    
    model_config = ConfigDict()