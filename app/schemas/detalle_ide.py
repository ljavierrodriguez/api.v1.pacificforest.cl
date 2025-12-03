from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class DetalleIdeCreate(BaseModel):
    id_ide: int = Field(..., description="Descripción de id_ide")
    id_plc: int = Field(..., description="Descripción de id_plc")
    fob: str = Field(..., description="Descripción de fob")
    identificador_contenedor: Optional[str] = None
    sello: Optional[str] = None
    peso_neto: Optional[str] = None
    peso_bruto: Optional[str] = None
    nro_linea: int = Field(..., description="Descripción de nro_linea")

    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "id_ide": 1,
                "id_plc": 1,
                "fob": "100.00",
                "nro_linea": 1,
            }
        ]
    })


class DetalleIdeRead(BaseModel):
    id_detalle_ide: int = Field(..., description="Descripción de id_detalle_ide")
    id_ide: int = Field(..., description="Descripción de id_ide")
    id_plc: int = Field(..., description="Descripción de id_plc")
    fob: str = Field(..., description="Descripción de fob")
    identificador_contenedor: Optional[str] = None
    sello: Optional[str] = None
    peso_neto: Optional[str] = None
    peso_bruto: Optional[str] = None
    nro_linea: int = Field(..., description="Descripción de nro_linea")

    model_config = ConfigDict(from_attributes=True)


class DetalleIdeUpdate(BaseModel):
    fob: Optional[str] = None
    identificador_contenedor: Optional[str] = None
    sello: Optional[str] = None
    peso_neto: Optional[str] = None
    peso_bruto: Optional[str] = None
    nro_linea: Optional[int] = None

    model_config = ConfigDict()
