from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class NavieraCreate(BaseModel):
    nombre: str = Field(..., description="Nombre de la naviera", max_length=100)

    model_config = ConfigDict(json_schema_extra={"examples": [{"nombre": "Maersk Line"}]})


class NavieraRead(BaseModel):
    id_naviera: int = Field(..., description="ID único de la naviera")
    nombre: str = Field(..., description="Nombre de la naviera")

    model_config = ConfigDict(from_attributes=True)


class NavieraUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    
    model_config = ConfigDict()