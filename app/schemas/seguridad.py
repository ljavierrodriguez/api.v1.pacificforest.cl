from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SeguridadBase(BaseModel):
    id_usuario: int = Field(..., description="ID del usuario")
    modulo: str = Field(..., max_length=15, description="Nombre del módulo")
    crear: bool = Field(default=False, description="Permiso para crear")
    ver: bool = Field(default=False, description="Permiso para ver")
    editar: bool = Field(default=False, description="Permiso para editar")
    eliminar: bool = Field(default=False, description="Permiso para eliminar")


class SeguridadCreate(SeguridadBase):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id_usuario": 1,
                    "modulo": "Proforma",
                    "crear": True,
                    "ver": True,
                    "editar": True,
                    "eliminar": False
                }
            ]
        }
    )


class SeguridadUpdate(BaseModel):
    id_usuario: Optional[int] = None
    modulo: Optional[str] = Field(None, max_length=15, description="Nombre del módulo")
    crear: Optional[bool] = None
    ver: Optional[bool] = None
    editar: Optional[bool] = None
    eliminar: Optional[bool] = None


class SeguridadRead(SeguridadBase):
    id_seguridad: int

    model_config = ConfigDict(from_attributes=True)

