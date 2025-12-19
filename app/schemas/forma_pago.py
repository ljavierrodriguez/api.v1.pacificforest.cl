from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class FormaPagoCreate(BaseModel):
    nombre: str = Field(..., description="Nombre de la forma de pago", max_length=50)
    por_defecto: Optional[bool] = False

    model_config = ConfigDict(json_schema_extra={"examples": [{"nombre": "Transferencia Bancaria", "por_defecto": True}]})


class FormaPagoRead(BaseModel):
    id_forma_pago: int = Field(..., description="ID único de la forma de pago")
    nombre: str = Field(..., description="Nombre de la forma de pago")
    por_defecto: bool = Field(..., description="Indica si es la forma de pago por defecto")

    model_config = ConfigDict(from_attributes=True)


class FormaPagoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=50)
    por_defecto: Optional[bool] = None
    
    model_config = ConfigDict()