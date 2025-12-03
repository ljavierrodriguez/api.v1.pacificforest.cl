from pydantic import BaseModel, ConfigDict, Field


class ParametroBase(BaseModel):
    nota_1: str = Field(..., description="Descripción de nota_1")


class ParametroCreate(ParametroBase):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"nota_1": "Texto de nota..."}]}
    )


class ParametroRead(ParametroBase):
    id_parametro: int

    model_config = ConfigDict(from_attributes=True)
