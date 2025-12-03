from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class EstadoProformaCreate(BaseModel):
    nombre: str = Field(..., description="Descripción de nombre")
    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {"nombre": "Pendiente"}
        ]
    })

class EstadoProformaRead(BaseModel):
    id_estado_proforma: int = Field(..., description="Descripción de id_estado_proforma")
    nombre: str = Field(..., description="Descripción de nombre")
    model_config = ConfigDict(from_attributes=True)

class EstadoProformaUpdate(BaseModel):
    nombre: Optional[str] = None
    model_config = ConfigDict()
