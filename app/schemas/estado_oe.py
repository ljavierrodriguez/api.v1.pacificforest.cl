from pydantic import BaseModel, ConfigDict, Field


class EstadoOeCreate(BaseModel):
    nombre: str = Field(..., description="Descripción de nombre")
    model_config = ConfigDict(json_schema_extra={"examples": [{"nombre": "Procesada"}]})


class EstadoOeRead(BaseModel):
    id_estado_oe: int = Field(..., description="Descripción de id_estado_oe")
    nombre: str = Field(..., description="Descripción de nombre")
    model_config = ConfigDict(from_attributes=True)


class EstadoOeUpdate(BaseModel):
    nombre: str | None = None
    model_config = ConfigDict()
