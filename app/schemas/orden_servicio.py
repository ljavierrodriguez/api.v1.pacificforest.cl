from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any
from datetime import date
from decimal import Decimal
from app.schemas.contacto_orden_servicio import ContactoOrdenServicioRead
from app.schemas.contacto_orden_servicio import (
    ContactoOrdenServicioRead,
    ContactoOrdenServicioCreate,
)


class DetalleOrdenServicioInOrdenRead(BaseModel):
    id_detalle_os: int
    id_orden_servicio: int
    id_producto: Optional[int] = None
    id_unidad_venta: Optional[int] = None
    texto_abierto: Optional[str] = None
    espesor: Optional[str] = None
    id_unidad_medida_espesor: Optional[int] = None
    ancho: Optional[str] = None
    id_unidad_medida_ancho: Optional[int] = None
    largo: Optional[str] = None
    id_unidad_medida_largo: Optional[int] = None
    cantidad: Optional[Decimal] = None
    precio_unitario: Decimal
    subtotal: Optional[Decimal] = None
    volumen: Optional[Decimal] = None
    volumen_eq: Optional[Decimal] = None
    precio_eq: Optional[Decimal] = None
    # Nombres de entidades relacionadas
    id_especie: Optional[int] = None
    especie_nombre: Optional[str] = None
    producto_nombre: Optional[str] = None
    unidad_venta_nombre: Optional[str] = None
    unidad_medida_espesor_nombre: Optional[str] = None
    unidad_medida_ancho_nombre: Optional[str] = None
    unidad_medida_largo_nombre: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OrdenServicioDetalleCreate(BaseModel):
    id_producto: Optional[int] = None
    id_especie: Optional[int] = None
    id_unidad_venta: Optional[int] = None
    texto_abierto: Optional[str] = Field(None, max_length=200)
    espesor: Optional[str] = Field(None, max_length=20)
    id_unidad_medida_espesor: Optional[int] = None
    ancho: Optional[str] = Field(None, max_length=20)
    id_unidad_medida_ancho: Optional[int] = None
    largo: Optional[str] = Field(None, max_length=20)
    id_unidad_medida_largo: Optional[int] = None
    cantidad: Optional[Decimal] = None
    precio_unitario: Decimal = Field(..., description="Precio unitario del servicio (requerido)")
    subtotal: Optional[Decimal] = None
    volumen: Optional[Decimal] = None
    volumen_eq: Optional[Decimal] = None
    precio_eq: Optional[Decimal] = None


class OrdenServicioCreate(BaseModel):
    fecha_emision: date = Field(..., description="Fecha de emisión de la orden de servicio")
    fecha_entrega: date = Field(..., description="Fecha de entrega")
    id_cliente_proveedor: int = Field(..., description="ID del proveedor")
    id_usuario_encargado: int = Field(..., description="ID del usuario encargado")
    id_usuario: int = Field(..., description="ID del usuario que crea la orden")
    servicio: str = Field(..., max_length=120, description="Tipo de servicio")
    destino: Optional[str] = Field(None, max_length=15)
    id_moneda: int = Field(..., description="ID de la moneda")
    id_empresa: Optional[int] = None
    id_orden_compra: Optional[int] = None
    id_direccion_proveedor: int = Field(..., description="ID de la dirección del proveedor")
    observacion: Optional[str] = None
    nota_1: Optional[str] = None
    otras_especificaciones: Optional[str] = None
    url_imagen: Optional[str] = Field(None, max_length=100)
    valor_neto: Decimal = Field(..., description="Valor neto de la orden")
    iva: Decimal = Field(..., description="IVA de la orden")
    tasa_iva: Optional[Decimal] = None
    valor_total: Decimal = Field(..., description="Valor total de la orden")
    flete: Optional[Decimal] = None
    id_estado_orden_servicio: int = Field(..., description="ID del estado de la orden de servicio")
    detalles: list[OrdenServicioDetalleCreate] = Field(
        ...,
        min_length=1,
        description="Detalles de la orden de servicio (mínimo 1 item requerido)",
    )
    contactos_orden_servicio: List[ContactoOrdenServicioCreate] = Field(default_factory=list)


class OrdenServicioRead(BaseModel):
    id_orden_servicio: int
    fecha_emision: date
    fecha_entrega: date
    id_cliente_proveedor: int
    id_usuario_encargado: int
    id_usuario: int
    servicio: str
    destino: Optional[str] = None
    id_moneda: int
    id_empresa: Optional[int] = None
    id_orden_compra: Optional[int] = None
    orden_compra_numero: Optional[int] = Field(None, description="Numero/ID de la orden de compra asociada")
    id_direccion_proveedor: int
    observacion: Optional[str] = None
    nota_1: Optional[str] = None
    otras_especificaciones: Optional[str] = None
    url_imagen: Optional[str] = None
    valor_neto: Decimal
    iva: Decimal
    tasa_iva: Optional[Decimal] = None
    valor_total: Decimal
    flete: Optional[Decimal] = None
    id_estado_orden_servicio: int

    volumenTotal: Optional[Decimal] = Field(0, description="Volumen total de la orden")

    proveedor_nombre: Optional[str] = Field(None, description="Nombre del proveedor")
    usuario_nombre: Optional[str] = Field(None, description="Nombre del usuario encargado")
    moneda_nombre: Optional[str] = Field(None, description="Nombre de la moneda")
    empresa_nombre: Optional[str] = Field(None, description="Nombre de la empresa")
    estado_nombre: Optional[str] = Field(None, description="Nombre del estado")
    detalles_orden_servicio: List[DetalleOrdenServicioInOrdenRead] = Field(default_factory=list)
    contactos_orden_servicio: List[ContactoOrdenServicioRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class OrdenServicioUpdate(BaseModel):
    fecha_emision: Optional[date] = None
    fecha_entrega: Optional[date] = None
    id_cliente_proveedor: Optional[int] = None
    id_usuario_encargado: Optional[int] = None
    id_usuario: Optional[int] = None
    servicio: Optional[str] = Field(None, max_length=120)
    destino: Optional[str] = Field(None, max_length=15)
    id_moneda: Optional[int] = None
    id_empresa: Optional[int] = None
    id_orden_compra: Optional[int] = None
    id_direccion_proveedor: Optional[int] = None
    observacion: Optional[str] = None
    nota_1: Optional[str] = None
    otras_especificaciones: Optional[str] = None
    url_imagen: Optional[str] = Field(None, max_length=100)
    valor_neto: Optional[Decimal] = None
    iva: Optional[Decimal] = None
    tasa_iva: Optional[Decimal] = None
    valor_total: Optional[Decimal] = None
    flete: Optional[Decimal] = None
    id_estado_orden_servicio: Optional[int] = None
    detalles: Optional[List[OrdenServicioDetalleCreate]] = None
    contactos_orden_servicio: List[ContactoOrdenServicioCreate] = Field(default_factory=list)
    model_config = ConfigDict()


class AsignarOrdenCompraPayload(BaseModel):
    id_orden_compra: int