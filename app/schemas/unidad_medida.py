from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class UnidadMedidaCreate(BaseModel):
    nombre: str = Field(..., description="Nombre de la unidad de medida", max_length=10)
    equivalencia_mm: str = Field(..., description="Equivalencia en milímetros", max_length=12)
    descripcion: str = Field(..., description="Descripción de la unidad de medida", max_length=100)
    por_defecto: Optional[bool] = False

    model_config = ConfigDict(json_schema_extra={"examples": [{"nombre": "mm", "equivalencia_mm": "1", "descripcion": "Milímetros", "por_defecto": True}]})


class UnidadMedidaRead(BaseModel):
    id_unidad_medida: int = Field(..., description="ID único de la unidad de medida")
    nombre: str = Field(..., description="Nombre de la unidad de medida")
    equivalencia_mm: str = Field(..., description="Equivalencia en milímetros")
    descripcion: str = Field(..., description="Descripción de la unidad de medida")
    por_defecto: bool = Field(..., description="Indica si es la unidad de medida por defecto")

    model_config = ConfigDict(from_attributes=True)


class UnidadMedidaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=10)
    equivalencia_mm: Optional[str] = Field(None, max_length=12)
    descripcion: Optional[str] = Field(None, max_length=100)
    por_defecto: Optional[bool] = None
    
    model_config = ConfigDict()