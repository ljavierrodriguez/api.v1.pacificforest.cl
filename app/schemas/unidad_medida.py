from pydantic import BaseModel, ConfigDict, Field, field_validator
from decimal import Decimal
from typing import Optional


class UnidadMedidaCreate(BaseModel):
    nombre: str = Field(..., description="Nombre de la unidad de medida", max_length=10)
    equivalencia_mm: str | Decimal = Field(..., description="Equivalencia en milímetros")
    descripcion: str = Field(..., description="Descripción de la unidad de medida", max_length=100)
    por_defecto: Optional[bool] = False

    @field_validator("equivalencia_mm", mode="before")
    @classmethod
    def _normalize_equivalencia_mm(cls, value):
        if value is None:
            return value
        normalized = str(value).strip()
        if len(normalized) > 12:
            raise ValueError("equivalencia_mm no puede tener más de 12 caracteres")
        return normalized

    model_config = ConfigDict(json_schema_extra={"examples": [{"nombre": "mm", "equivalencia_mm": "1", "descripcion": "Milímetros", "por_defecto": True}]})


class UnidadMedidaRead(BaseModel):
    id_unidad_medida: int = Field(..., description="ID único de la unidad de medida")
    nombre: str = Field(..., description="Nombre de la unidad de medida")
    equivalencia_mm: str = Field(..., description="Equivalencia en milímetros")
    descripcion: str = Field(..., description="Descripción de la unidad de medida")
    por_defecto: bool = Field(..., description="Indica si es la unidad de medida por defecto")

    @field_validator("equivalencia_mm", mode="before")
    @classmethod
    def _normalize_equivalencia_mm(cls, value):
        # Algunas bases devuelven este campo como Decimal; se normaliza a string.
        return str(value) if value is not None else value

    model_config = ConfigDict(from_attributes=True)


class UnidadMedidaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=10)
    equivalencia_mm: Optional[str | Decimal] = Field(None)
    descripcion: Optional[str] = Field(None, max_length=100)
    por_defecto: Optional[bool] = None

    @field_validator("equivalencia_mm", mode="before")
    @classmethod
    def _normalize_equivalencia_mm(cls, value):
        if value is None:
            return value
        normalized = str(value).strip()
        if len(normalized) > 12:
            raise ValueError("equivalencia_mm no puede tener más de 12 caracteres")
        return normalized
    
    model_config = ConfigDict()