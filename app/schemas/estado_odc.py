from pydantic import BaseModel, ConfigDict, Field


class EstadoOdcCreate(BaseModel):
    nombre: str = Field(..., description="Descripción de nombre")
    model_config = ConfigDict(json_schema_extra={"examples": [{"nombre": "Abierta"}]})


class EstadoOdcRead(BaseModel):
    id_estado_odc: int = Field(..., description="Descripción de id_estado_odc")
    nombre: str = Field(..., description="Descripción de nombre")
    model_config = ConfigDict(from_attributes=True)


class EstadoOdcUpdate(BaseModel):
    nombre: str | None = None
    model_config = ConfigDict()
