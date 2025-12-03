from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class AgenteBase(BaseModel):
    id_pais: int = Field(..., description="Descripción de id_pais")
    nombre: str = Field(..., description="Descripción de nombre")
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    por_defecto: Optional[bool] = False


class AgenteCreate(AgenteBase):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id_pais": 1,
                    "nombre": "Agente Ejemplo",
                    "correo": "agente@example.com",
                    "telefono": "+56912345678",
                    "por_defecto": False
                }
            ]
        }
    )


class AgenteUpdate(BaseModel):
    id_pais: Optional[int] = None
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    por_defecto: Optional[bool] = None


class AgenteRead(AgenteBase):
    id_agente: int

    model_config = ConfigDict(from_attributes=True)
