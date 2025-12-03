from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class EspecieBase(BaseModel):
    nombre_esp: str = Field(..., description="Descripción de nombre_esp")
    nombre_ing: str = Field(..., description="Descripción de nombre_ing")
    descripcion: Optional[str] = None
    por_defecto: Optional[bool] = False
    url_imagen: Optional[str] = None


class EspecieCreate(EspecieBase):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "nombre_esp": "ESPECIE EJEMPLO",
                    "nombre_ing": "SPECIES EXAMPLE",
                    "descripcion": "Descripción...",
                    "por_defecto": False,
                    "url_imagen": None,
                }
            ]
        }
    )


class EspecieRead(EspecieBase):
    id_especie: int

    model_config = ConfigDict(from_attributes=True)


class EspecieUpdate(EspecieBase):
    nombre_esp: Optional[str]
    nombre_ing: Optional[str]
