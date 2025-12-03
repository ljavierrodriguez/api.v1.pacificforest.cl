from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date


class PlcCreate(BaseModel):
    id_operacion_exportacion: Optional[int] = None
    id_estado_pl: int = Field(..., description="Descripción de id_estado_pl")
    fecha_creacion: date = Field(..., description="Descripción de fecha_creacion")
    volumen_m3: Optional[str] = None
    paquetes: int = Field(..., description="Descripción de paquetes")
    peso_bruto: str = Field(..., description="Descripción de peso_bruto")
    piezas: int = Field(..., description="Descripción de piezas")
    descripcion: str = Field(..., description="Descripción de descripcion")
    categoria_fsc: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={"examples": [{
        "id_operacion_exportacion": 1,
        "id_estado_pl": 1,
        "fecha_creacion": "2025-12-01",
        "paquetes": 10,
        "peso_bruto": "1000",
        "piezas": 100,
        "descripcion": "PLC ejemplo"
    }]})


class PlcRead(BaseModel):
    id_plc: int = Field(..., description="Descripción de id_plc")
    id_operacion_exportacion: Optional[int] = Field(default=None, description="Descripción de id_operacion_exportacion")
    id_estado_pl: int = Field(..., description="Descripción de id_estado_pl")
    fecha_creacion: date = Field(..., description="Descripción de fecha_creacion")
    paquetes: int = Field(..., description="Descripción de paquetes")
    model_config = ConfigDict(from_attributes=True)


class PlcUpdate(BaseModel):
    id_estado_pl: Optional[int] = None
    fecha_creacion: Optional[date] = None
    paquetes: Optional[int] = None
    model_config = ConfigDict()
