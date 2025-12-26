from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class PuertoCreate(BaseModel):
    nombre: str = Field(..., description="Nombre del puerto")
    #codigo: Optional[str] = Field(None, description="Código del puerto")
    descripcion: Optional[str] = Field(None, description="Descripción del puerto")
    model_config = ConfigDict(json_schema_extra={"examples": [{"nombre": "Valparaíso", "codigo": "VL", "descripcion": "Puerto principal de Chile"}]})


class PuertoRead(BaseModel):
    id_puerto: int = Field(..., description="ID único del puerto")
    nombre: str = Field(..., description="Nombre del puerto")
    #codigo: Optional[str] = Field(default=None, description="Código del puerto")
    descripcion: Optional[str] = Field(default=None, description="Descripción del puerto")
    model_config = ConfigDict(from_attributes=True)


class PuertoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, description="Nombre del puerto")
    #codigo: Optional[str] = Field(None, description="Código del puerto")
    descripcion: Optional[str] = Field(None, description="Descripción del puerto")
    model_config = ConfigDict()
