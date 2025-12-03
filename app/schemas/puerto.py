from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class PuertoCreate(BaseModel):
    nombre: str = Field(..., description="Descripción de nombre")
    codigo: Optional[str] = None
    model_config = ConfigDict(json_schema_extra={"examples": [{"nombre": "Valparaíso", "codigo": "VL"}]})


class PuertoRead(BaseModel):
    id_puerto: int = Field(..., description="Descripción de id_puerto")
    nombre: str = Field(..., description="Descripción de nombre")
    codigo: Optional[str] = Field(default=None, description="Descripción de codigo")
    model_config = ConfigDict(from_attributes=True)


class PuertoUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    model_config = ConfigDict()
