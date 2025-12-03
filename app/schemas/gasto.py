from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from decimal import Decimal


class GastoCreate(BaseModel):
    descripcion: str = Field(..., description="Descripción de descripcion")
    monto: Decimal = Field(..., description="Descripción de monto")
    model_config = ConfigDict(json_schema_extra={"examples": [{"descripcion": "Gasto de envío", "monto": "123.45"}]})


class GastoRead(BaseModel):
    id_gasto: int = Field(..., description="Descripción de id_gasto")
    descripcion: str = Field(..., description="Descripción de descripcion")
    monto: Decimal = Field(..., description="Descripción de monto")
    model_config = ConfigDict(from_attributes=True)


class GastoUpdate(BaseModel):
    descripcion: Optional[str] = None
    monto: Optional[Decimal] = None
    model_config = ConfigDict()
