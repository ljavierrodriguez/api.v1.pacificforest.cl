from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Optional
from datetime import date
from decimal import Decimal

from app.schemas.cliente_proveedor import ClienteProveedorRead
from app.schemas.direccion import DireccionRead
from app.schemas.puerto import PuertoRead


class ProformaCreate(BaseModel):
    id_operacion_exportacion: Optional[int] = Field(None, description="ID de la operación de exportación")
    id_contenedor: Optional[int] = Field(None, description="ID del contenedor")
    id_usuario_encargado: Optional[int] = Field(None, description="ID del usuario encargado")
    id_estado_proforma: Optional[int] = Field(None, description="ID del estado de la proforma")
    id_moneda: Optional[int] = Field(None, description="ID de la moneda")
    id_agente: Optional[int] = Field(None, description="ID del agente")
    id_tipo_comision: Optional[int] = Field(None, description="ID del tipo de comisión")
    id_clausula_venta: Optional[str] = Field(None, description="ID de la cláusula de venta")
    cantidad_contenedor: Optional[int] = Field(None, description="Cantidad de contenedores")
    fecha_emision: date = Field(..., description="Fecha de emisión de la proforma")
    fecha_aceptacion: Optional[date] = Field(None, description="Fecha de aceptación")
    fecha_entrega: Optional[date] = Field(None, description="Fecha de entrega")
    valor_flete: Optional[Decimal] = Field(None, description="Valor del flete")
    especificaciones: Optional[str] = Field(None, description="Especificaciones", max_length=2000)
    nota: Optional[str] = Field(None, description="Nota", max_length=2000)
    nota_1: Optional[str] = Field(None, description="Nota 1", max_length=2000)
    nota_2: Optional[str] = Field(None, description="Nota 2", max_length=2000)
    url_imagen: Optional[str] = Field(None, description="URL de la imagen", max_length=100)
    id_empresa: int = Field(..., description="ID de la empresa")
    id_direccion_facturar: int = Field(..., description="ID de la dirección de facturación")
    id_direccion_consignar: int = Field(..., description="ID de la dirección de consignación")
    id_direccion_notificar: int = Field(..., description="ID de la dirección de notificación")

    model_config = ConfigDict(json_schema_extra={
        "examples": [{
            "fecha_emision": "2025-12-01",
            "id_empresa": 1,
            "id_direccion_facturar": 1,
            "id_direccion_consignar": 1,
            "id_direccion_notificar": 1,
            "especificaciones": "Especificaciones de la proforma",
            "valor_flete": "1000.50"
        }]
    })


class ProformaRead(BaseModel):
    id_proforma: int = Field(..., description="ID único de la proforma")
    id_operacion_exportacion: Optional[int] = Field(None, description="ID de la operación de exportación")
    id_contenedor: Optional[int] = Field(None, description="ID del contenedor")
    id_usuario_encargado: Optional[int] = Field(None, description="ID del usuario encargado")
    id_estado_proforma: Optional[int] = Field(None, description="ID del estado de la proforma")
    id_moneda: Optional[int] = Field(None, description="ID de la moneda")
    id_agente: Optional[int] = Field(None, description="ID del agente")
    id_tipo_comision: Optional[int] = Field(None, description="ID del tipo de comisión")
    id_clausula_venta: Optional[str] = Field(None, description="ID de la cláusula de venta")
    cantidad_contenedor: Optional[int] = Field(None, description="Cantidad de contenedores")
    fecha_emision: date = Field(..., description="Fecha de emisión de la proforma")
    fecha_aceptacion: Optional[date] = Field(None, description="Fecha de aceptación")
    fecha_entrega: Optional[date] = Field(None, description="Fecha de entrega")
    valor_flete: Optional[Decimal] = Field(None, description="Valor del flete")
    especificaciones: Optional[str] = Field(None, description="Especificaciones")
    nota: Optional[str] = Field(None, description="Nota")
    nota_1: Optional[str] = Field(None, description="Nota 1")
    nota_2: Optional[str] = Field(None, description="Nota 2")
    url_imagen: Optional[str] = Field(None, description="URL de la imagen")
    id_empresa: int = Field(..., description="ID de la empresa")
    id_direccion_facturar: int = Field(..., description="ID de la dirección de facturación")
    id_direccion_consignar: int = Field(..., description="ID de la dirección de consignación")
    id_direccion_notificar: int = Field(..., description="ID de la dirección de notificación")
    id: int = Field(..., description="ID de la proforma")
    numero_proforma: int = Field(..., description="Número de la proforma")
    numeroProforma: int = Field(..., description="Número de la proforma (alias)")
    oe_numero: Optional[int] = Field(None, description="Número de la operación de exportación")
    numero_operacion: Optional[int] = Field(None, description="Número de la operación de exportación (alias)")
    facturar_a: Optional[int] = Field(None, description="ID del cliente a facturar")
    consignar_a: Optional[int] = Field(None, description="ID del cliente a consignar")
    notificar_a: Optional[int] = Field(None, description="ID del cliente a notificar")
    id_cliente_facturar: Optional[int] = Field(None, description="ID del cliente a facturar (alias)")
    id_cliente_consignar: Optional[int] = Field(None, description="ID del cliente a consignar (alias)")
    id_cliente_notificar: Optional[int] = Field(None, description="ID del cliente a notificar (alias)")
    totalDinero: Optional[Decimal] = Field(None, description="Total de dinero de la proforma")
    puertoOrigen: Optional[str] = Field(None, description="Nombre del puerto de origen (alias)")
    puertoDestino: Optional[str] = Field(None, description="Nombre del puerto de destino (alias)")
    formaPago: Optional[str] = Field(None, description="Nombre de la forma de pago (alias)")
    
    # Campos calculados añadidos para optimizar el listado
    volumenTotal: Optional[Decimal] = Field(0, description="Volumen total de la proforma")
    volumenAsignado: Optional[Decimal] = Field(0, description="Volumen asignado en OCs")
    volumenAbastecido: Optional[Decimal] = Field(0, description="Volumen abastecido (OCs normales + OS desde OCs directas)")
    volumenDesdeOc: Optional[Decimal] = Field(0, description="Volumen abastecido desde OCs normales")
    volumenDesdeOs: Optional[Decimal] = Field(0, description="Volumen abastecido desde OS de OCs directas")
    volumenPendiente: Optional[Decimal] = Field(0, description="Volumen pendiente")
    oc_asociadas: Optional[int] = Field(0, description="Cantidad de OCs asociadas")
    estadoFlujo: Optional[str] = Field('sin-oc', description="Estado del flujo (sin-oc, parcial, completado)")

    # Etiquetas de texto para evitar buscar en mantenedores del frontend
    empresa_nombre: Optional[str] = Field(None, description="Nombre de la empresa")
    moneda_nombre: Optional[str] = Field(None, description="Etiqueta o nombre de la moneda")
    estado_nombre: Optional[str] = Field(None, description="Nombre del estado")
    usuario_nombre: Optional[str] = Field(None, description="Nombre del usuario encargado")
    forma_pago_nombre: Optional[str] = Field(None, description="Nombre de la forma de pago")
    facturar_a_nombre: Optional[str] = Field(None, description="Nombre del cliente a facturar")
    consignar_a_nombre: Optional[str] = Field(None, description="Nombre del cliente a consignar")
    notificar_a_nombre: Optional[str] = Field(None, description="Nombre del cliente a notificar")
    puerto_origen_nombre: Optional[str] = Field(None, description="Nombre del puerto de origen")
    puerto_destino_nombre: Optional[str] = Field(None, description="Nombre del puerto de destino")
    id_puerto_origen: Optional[int] = Field(None, description="ID del puerto de origen")
    id_puerto_destino: Optional[int] = Field(None, description="ID del puerto de destino")
    id_forma_pago: Optional[int] = Field(None, description="ID de la forma de pago")

    model_config = ConfigDict(from_attributes=True)


class ProformaDetalleItemRead(BaseModel):
    id_detalle_proforma: int = Field(..., description="ID del detalle de proforma")
    id_producto: Optional[int] = Field(None, description="ID del producto")
    especie_nombre: Optional[str] = Field(None, description="Nombre de la especie")
    producto_nombre: Optional[str] = Field(None, description="Nombre del producto")
    texto_libre: Optional[str] = Field(None, description="Texto libre")
    id_unidad_venta: int = Field(..., description="ID de la unidad de venta")
    cantidad: Decimal = Field(..., description="Cantidad")
    espesor: Optional[str] = Field(None, description="Espesor")
    id_unidad_medida_espesor: Optional[int] = Field(None, description="ID unidad medida espesor")
    ancho: Optional[str] = Field(None, description="Ancho")
    id_unidad_medida_ancho: Optional[int] = Field(None, description="ID unidad medida ancho")
    largo: Optional[str] = Field(None, description="Largo")
    id_unidad_medida_largo: Optional[int] = Field(None, description="ID unidad medida largo")
    piezas: Optional[int] = Field(None, description="Piezas")
    precio_unitario: Decimal = Field(..., description="Precio unitario")
    subtotal: Decimal = Field(..., description="Subtotal")
    volumen_eq: Decimal = Field(..., description="Volumen equivalente")
    precio_eq: Decimal = Field(..., description="Precio equivalente")

    model_config = ConfigDict(from_attributes=True)


class ProformaOrdenCompraEmbeddedRead(BaseModel):
    id_orden_compra: int = Field(..., description="ID de la orden de compra")
    proveedor_nombre: Optional[str] = Field(None, description="Nombre del proveedor")
    fecha_emision: date = Field(..., description="Fecha de emision")
    volumenTotal: Decimal = Field(..., description="Volumen total de la OC")
    estado_nombre: Optional[str] = Field(None, description="Nombre del estado ODC")
    id_estado_odc: int = Field(..., description="ID del estado ODC")
    vinculado: Optional[int] = Field(None, description="Flag de vinculacion")
    tipo: Optional[str] = Field(None, description="Tipo de OC (Normal o Directa/Asignada)")
    ordenes_servicio: list["ProformaOrdenServicioEmbeddedRead"] = Field(
        default_factory=list,
        description="OS asociadas cuando la OC es directa/asignada",
    )

    model_config = ConfigDict(from_attributes=True)


class ProformaOrdenServicioEmbeddedRead(BaseModel):
    id_orden_servicio: int = Field(..., description="ID de la orden de servicio")
    estado_nombre: Optional[str] = Field(None, description="Nombre del estado de la OS")
    id_estado_orden_servicio: Optional[int] = Field(None, description="ID del estado de la OS")
    volumenProducido: Decimal = Field(..., description="Volumen producido por la OS")

    model_config = ConfigDict(from_attributes=True)


class ProformaContactoEmbeddedRead(BaseModel):
    id_contacto: int = Field(..., description="ID del contacto")
    nombre: str = Field(..., description="Nombre del contacto")
    correo: Optional[str] = Field(None, description="Correo del contacto")
    telefono: Optional[str] = Field(None, description="Telefono del contacto")

    model_config = ConfigDict(from_attributes=True)


class ProformaDetailRead(ProformaRead):
    consignar_a_nombre: Optional[str] = Field(None, description="Nombre del cliente a consignar")
    notificar_a_nombre: Optional[str] = Field(None, description="Nombre del cliente a notificar")
    puerto_origen_nombre: Optional[str] = Field(None, description="Nombre del puerto de origen")
    puerto_destino_nombre: Optional[str] = Field(None, description="Nombre del puerto de destino")
    forma_pago_nombre: Optional[str] = Field(None, description="Nombre de la forma de pago")
    agente_nombre: Optional[str] = Field(None, description="Nombre del agente")
    tipo_comision_nombre: Optional[str] = Field(None, description="Nombre del tipo de comisión")
    clausula_venta_nombre: Optional[str] = Field(None, description="Cláusula de venta (FOB, CIF, etc.)")

    facturar_a_id: Optional[int] = Field(None, description="ID del cliente a facturar")
    consignar_a_id: Optional[int] = Field(None, description="ID del cliente a consignar")
    notificar_a_id: Optional[int] = Field(None, description="ID del cliente a notificar")
    facturar_a_cliente: Optional[ClienteProveedorRead] = Field(None, description="Cliente a facturar")
    consignar_a_cliente: Optional[ClienteProveedorRead] = Field(None, description="Cliente a consignar")
    notificar_a_cliente: Optional[ClienteProveedorRead] = Field(None, description="Cliente a notificar")
    direccion_facturar: Optional[DireccionRead] = Field(None, description="Dirección de facturación")
    direccion_consignar: Optional[DireccionRead] = Field(None, description="Dirección de consignación")
    direccion_notificar: Optional[DireccionRead] = Field(None, description="Dirección de notificación")
    puerto_origen: Optional[PuertoRead] = Field(None, description="Puerto de origen")
    puerto_destino: Optional[PuertoRead] = Field(None, description="Puerto de destino")

    detalles: list[ProformaDetalleItemRead] = Field(default_factory=list, description="Detalles de productos de la proforma")
    ordenes_compra: list[ProformaOrdenCompraEmbeddedRead] = Field(default_factory=list, description="Ordenes de compra asociadas")
    ordenes_servicio: list[ProformaOrdenServicioEmbeddedRead] = Field(default_factory=list, description="Ordenes de servicio asociadas via OCs directas")
    contactos: list[ProformaContactoEmbeddedRead] = Field(default_factory=list, description="Contactos asociados a la proforma")


class ProformaUpdate(BaseModel):
    id_operacion_exportacion: Optional[int] = Field(None, description="ID de la operación de exportación")
    id_contenedor: Optional[int] = Field(None, description="ID del contenedor")
    id_usuario_encargado: Optional[int] = Field(None, description="ID del usuario encargado")
    id_estado_proforma: Optional[int] = Field(None, description="ID del estado de la proforma")
    id_moneda: Optional[int] = Field(None, description="ID de la moneda")
    id_agente: Optional[int] = Field(None, description="ID del agente")
    id_tipo_comision: Optional[int] = Field(None, description="ID del tipo de comisión")
    id_clausula_venta: Optional[str] = Field(None, description="ID de la cláusula de venta")
    cantidad_contenedor: Optional[int] = Field(None, description="Cantidad de contenedores")
    fecha_emision: Optional[date] = Field(None, description="Fecha de emisión de la proforma")
    fecha_aceptacion: Optional[date] = Field(None, description="Fecha de aceptación")
    fecha_entrega: Optional[date] = Field(None, description="Fecha de entrega")
    valor_flete: Optional[Decimal] = Field(None, description="Valor del flete")
    especificaciones: Optional[str] = Field(None, description="Especificaciones", max_length=2000)
    nota: Optional[str] = Field(None, description="Nota", max_length=2000)
    nota_1: Optional[str] = Field(None, description="Nota 1", max_length=2000)
    nota_2: Optional[str] = Field(None, description="Nota 2", max_length=2000)
    url_imagen: Optional[str] = Field(None, description="URL de la imagen", max_length=100)
    id_empresa: Optional[int] = Field(None, description="ID de la empresa")
    id_direccion_facturar: Optional[int] = Field(None, description="ID de la dirección de facturación")
    id_direccion_consignar: Optional[int] = Field(None, description="ID de la dirección de consignación")
    id_direccion_notificar: Optional[int] = Field(None, description="ID de la dirección de notificación")

    model_config = ConfigDict()


# Asegura que Pydantic resuelva referencias adelantadas en runtime (FastAPI + TypeAdapter).
ProformaOrdenCompraEmbeddedRead.model_rebuild()
ProformaDetailRead.model_rebuild()
