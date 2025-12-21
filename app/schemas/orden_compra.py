from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date
from decimal import Decimal


class OrdenCompraCreate(BaseModel):
    id_proforma: Optional[int] = None
    id_proforma_anterior: Optional[int] = None
    fecha_emision: date = Field(..., description="Fecha de emisión de la orden de compra")
    id_cliente_proveedor: int = Field(..., description="ID del cliente/proveedor")
    id_usuario_encargado: int = Field(..., description="ID del usuario encargado")
    fecha_entrega: date = Field(..., description="Fecha de entrega")
    id_bodega: int = Field(..., description="ID de la bodega")
    destino: Optional[str] = Field(None, max_length=15)
    id_moneda: int = Field(..., description="ID de la moneda")
    id_empresa: Optional[int] = None
    ajustar_volumen: Optional[bool] = False
    observacion: Optional[str] = Field(None, max_length=1000)
    id_usuario: int = Field(..., description="ID del usuario que crea la orden")
    nota_1: Optional[str] = Field(None, max_length=1000)
    otras_especificaciones: Optional[str] = Field(None, max_length=1000)
    url_imagen: Optional[str] = Field(None, max_length=100)
    valor_neto: Decimal = Field(..., description="Valor neto de la orden")
    iva: Decimal = Field(..., description="IVA de la orden")
    tasa_iva: Optional[Decimal] = None
    valor_total: Decimal = Field(..., description="Valor total de la orden")
    id_estado_odc: int = Field(..., description="ID del estado de la orden de compra")
    id_direccion_proveedor: int = Field(..., description="ID de la dirección del proveedor")
    vinculado: Optional[int] = None

    model_config = ConfigDict(json_schema_extra={"examples": [{"fecha_emision": "2024-01-15", "id_cliente_proveedor": 1, "id_usuario_encargado": 1, "fecha_entrega": "2024-02-15", "id_bodega": 1, "id_moneda": 1, "id_usuario": 1, "valor_neto": 1000.00, "iva": 190.00, "valor_total": 1190.00, "id_estado_odc": 1, "id_direccion_proveedor": 1}]})


class OrdenCompraRead(BaseModel):
    id_orden_compra: int = Field(..., description="ID único de la orden de compra")
    id_proforma: Optional[int] = None
    id_proforma_anterior: Optional[int] = None
    fecha_emision: date = Field(..., description="Fecha de emisión")
    id_cliente_proveedor: int = Field(..., description="ID del cliente/proveedor")
    id_usuario_encargado: int = Field(..., description="ID del usuario encargado")
    fecha_entrega: date = Field(..., description="Fecha de entrega")
    id_bodega: int = Field(..., description="ID de la bodega")
    destino: Optional[str] = None
    id_moneda: int = Field(..., description="ID de la moneda")
    id_empresa: Optional[int] = None
    ajustar_volumen: bool = Field(..., description="Indica si se ajusta el volumen")
    observacion: Optional[str] = None
    id_usuario: int = Field(..., description="ID del usuario")
    nota_1: Optional[str] = None
    otras_especificaciones: Optional[str] = None
    url_imagen: Optional[str] = None
    valor_neto: Decimal = Field(..., description="Valor neto")
    iva: Decimal = Field(..., description="IVA")
    tasa_iva: Optional[Decimal] = None
    valor_total: Decimal = Field(..., description="Valor total")
    id_estado_odc: int = Field(..., description="ID del estado")
    id_direccion_proveedor: int = Field(..., description="ID de la dirección del proveedor")
    vinculado: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class OrdenCompraUpdate(BaseModel):
    id_proforma: Optional[int] = None
    id_proforma_anterior: Optional[int] = None
    fecha_emision: Optional[date] = None
    id_cliente_proveedor: Optional[int] = None
    id_usuario_encargado: Optional[int] = None
    fecha_entrega: Optional[date] = None
    id_bodega: Optional[int] = None
    destino: Optional[str] = Field(None, max_length=15)
    id_moneda: Optional[int] = None
    id_empresa: Optional[int] = None
    ajustar_volumen: Optional[bool] = None
    observacion: Optional[str] = Field(None, max_length=1000)
    id_usuario: Optional[int] = None
    nota_1: Optional[str] = Field(None, max_length=1000)
    otras_especificaciones: Optional[str] = Field(None, max_length=1000)
    url_imagen: Optional[str] = Field(None, max_length=100)
    valor_neto: Optional[Decimal] = None
    iva: Optional[Decimal] = None
    tasa_iva: Optional[Decimal] = None
    valor_total: Optional[Decimal] = None
    id_estado_odc: Optional[int] = None
    id_direccion_proveedor: Optional[int] = None
    vinculado: Optional[int] = None
    
    model_config = ConfigDict()