from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class DetalleProformaCreate(BaseModel):
    id_proforma: int = Field(..., description="Descripción de id_proforma")
    id_producto: Optional[int] = None
    id_unidad_venta: int = Field(..., description="Descripción de id_unidad_venta")
    cantidad: str = Field(..., description="Descripción de cantidad")
    precio_unitario: str = Field(..., description="Descripción de precio_unitario")
    subtotal: str = Field(..., description="Descripción de subtotal")
    volumen_eq: str = Field(..., description="Descripción de volumen_eq")
    precio_eq: str = Field(..., description="Descripción de precio_eq")

    model_config = ConfigDict(json_schema_extra={"examples": [{
        "id_proforma": 1,
        "id_unidad_venta": 1,
        "cantidad": "10",
        "precio_unitario": "100",
        "subtotal": "1000",
        "volumen_eq": "1.234",
        "precio_eq": "100"
    }]})


class DetalleProformaRead(BaseModel):
    id_detalle_proforma: int = Field(..., description="Descripción de id_detalle_proforma")
    id_proforma: int = Field(..., description="Descripción de id_proforma")
    id_producto: Optional[int] = Field(default=None, description="Descripción de id_producto")
    id_unidad_venta: int = Field(..., description="Descripción de id_unidad_venta")
    cantidad: str = Field(..., description="Descripción de cantidad")
    precio_unitario: str = Field(..., description="Descripción de precio_unitario")

    model_config = ConfigDict(from_attributes=True)


class DetalleProformaUpdate(BaseModel):
    cantidad: Optional[str] = None
    precio_unitario: Optional[str] = None
    subtotal: Optional[str] = None
    model_config = ConfigDict()
