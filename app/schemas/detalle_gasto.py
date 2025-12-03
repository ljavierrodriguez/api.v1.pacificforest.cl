from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class DetalleGastoCreate(BaseModel):
    id_gasto: Optional[int] = None
    id_profit_and_loss: int = Field(..., description="Descripción de id_profit_and_loss")
    valor: str = Field(..., description="Descripción de valor")
    nro_documento: Optional[str] = None
    pagado: bool = Field(..., description="Descripción de pagado")

    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "id_profit_and_loss": 1,
                "valor": "150.00",
                "nro_documento": "F123",
                "pagado": False,
            }
        ]
    })


class DetalleGastoRead(BaseModel):
    id_detalle_gasto: int = Field(..., description="Descripción de id_detalle_gasto")
    id_gasto: Optional[int] = None
    id_profit_and_loss: int = Field(..., description="Descripción de id_profit_and_loss")
    valor: str = Field(..., description="Descripción de valor")
    nro_documento: Optional[str] = None
    pagado: bool = Field(..., description="Descripción de pagado")

    model_config = ConfigDict(from_attributes=True)


class DetalleGastoUpdate(BaseModel):
    id_gasto: Optional[int] = None
    id_profit_and_loss: Optional[int] = None
    valor: Optional[str] = None
    nro_documento: Optional[str] = None
    pagado: Optional[bool] = None

    model_config = ConfigDict()
