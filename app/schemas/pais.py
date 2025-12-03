from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PaisBase(BaseModel):
    nombre: str = Field(..., description="Descripción de nombre")


class PaisCreate(PaisBase):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"nombre": "CHILE"}
            ]
        }
    )


class PaisRead(PaisBase):
    id_pais: int

    model_config = ConfigDict(from_attributes=True)


class PaisUpdate(BaseModel):
    nombre: Optional[str] = None
