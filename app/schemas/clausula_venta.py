from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class ClausulaVentaCreate(BaseModel):
    texto: str = Field(..., description="Descripción de texto")
    model_config = ConfigDict(json_schema_extra={"examples": [{"texto": "Condiciones de venta"}]})


class ClausulaVentaRead(BaseModel):
    id_clausula_venta: int = Field(..., description="Descripción de id_clausula_venta")
    texto: str = Field(..., description="Descripción de texto")
    model_config = ConfigDict(from_attributes=True)


class ClausulaVentaUpdate(BaseModel):
    texto: Optional[str] = None
    model_config = ConfigDict()
