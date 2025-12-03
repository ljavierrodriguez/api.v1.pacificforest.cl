from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class DetalleFacturaCreate(BaseModel):
    id_factura: int = Field(..., description="Descripción de id_factura")
    cantidad: str = Field(..., description="Descripción de cantidad")
    especificaciones: str = Field(..., description="Descripción de especificaciones")
    precio_unitario: str = Field(..., description="Descripción de precio_unitario")
    total: str = Field(..., description="Descripción de total")

    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "id_factura": 1,
                "cantidad": "10",
                "especificaciones": "Producto A",
                "precio_unitario": "100.00",
                "total": "1000.00",
            }
        ]
    })


class DetalleFacturaRead(BaseModel):
    id_detalle_factura: int = Field(..., description="Descripción de id_detalle_factura")
    id_factura: int = Field(..., description="Descripción de id_factura")
    cantidad: str = Field(..., description="Descripción de cantidad")
    especificaciones: str = Field(..., description="Descripción de especificaciones")
    precio_unitario: str = Field(..., description="Descripción de precio_unitario")
    total: str = Field(..., description="Descripción de total")

    model_config = ConfigDict(from_attributes=True)


class DetalleFacturaUpdate(BaseModel):
    cantidad: Optional[str] = None
    especificaciones: Optional[str] = None
    precio_unitario: Optional[str] = None
    total: Optional[str] = None

    model_config = ConfigDict()
