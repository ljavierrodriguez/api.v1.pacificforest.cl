from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DireccionBase(BaseModel):
    direccion: str = Field(..., description="Descripción de direccion")
    id_ciudad: int = Field(..., description="Descripción de id_ciudad")
    continente: Optional[str] = None
    fono_1: Optional[str] = None
    fono_2: Optional[str] = None
    id_cliente_proveedor: int = Field(..., description="Descripción de id_cliente_proveedor")
    por_defecto: bool = False


class DireccionCreate(DireccionBase):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "direccion": "Calle Falsa 123",
                    "id_ciudad": 1,
                    "continente": "AMERICA",
                    "fono_1": "+56912345678",
                    "id_cliente_proveedor": 1,
                    "por_defecto": False,
                }
            ]
        }
    )


class DireccionRead(DireccionBase):
    id_direccion: int

    model_config = ConfigDict(from_attributes=True)


class DireccionUpdate(DireccionBase):
    direccion: Optional[str]
    id_ciudad: Optional[int]
