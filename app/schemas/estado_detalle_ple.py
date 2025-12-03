from pydantic import BaseModel, ConfigDict, Field


class EstadoDetallePleBase(BaseModel):
    nombre: str = Field(..., description="Descripción de nombre")


class EstadoDetallePleCreate(EstadoDetallePleBase):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"nombre": "ACTIVO"}]}
    )


class EstadoDetallePleRead(EstadoDetallePleBase):
    id_estado_detalle_ple: int

    model_config = ConfigDict(from_attributes=True)
