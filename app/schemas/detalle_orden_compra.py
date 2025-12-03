from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class DetalleOrdenCompraCreate(BaseModel):
    id_orden_compra: int = Field(..., description="Descripción de id_orden_compra")
    id_producto: Optional[int] = None
    id_unidad_venta: Optional[int] = None
    texto_abierto: Optional[str] = None
    espesor: Optional[str] = None
    id_unidad_medida_espesor: Optional[int] = None
    ancho: Optional[str] = None
    id_unidad_medida_ancho: Optional[int] = None
    largo: Optional[str] = None
    id_unidad_medida_largo: Optional[int] = None
    cantidad: Optional[float] = None
    precio_unitario: Optional[float] = None
    subtotal: Optional[float] = None
    volumen: Optional[float] = None
    volumen_eq: Optional[float] = None
    precio_eq: Optional[float] = None

    model_config = ConfigDict(json_schema_extra={"examples": [{"id_orden_compra": 1, "cantidad": 10}]})


class DetalleOrdenCompraRead(BaseModel):
    id_detalle_odc: int = Field(..., description="Descripción de id_detalle_odc")
    id_orden_compra: int = Field(..., description="Descripción de id_orden_compra")
    id_producto: Optional[int] = None
    id_unidad_venta: Optional[int] = None
    texto_abierto: Optional[str] = None
    cantidad: Optional[float] = None
    precio_unitario: Optional[float] = None
    subtotal: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class DetalleOrdenCompraUpdate(BaseModel):
    texto_abierto: Optional[str] = None
    cantidad: Optional[float] = None
    precio_unitario: Optional[float] = None

    model_config = ConfigDict()
