from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date
from decimal import Decimal


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
    
    # Campos calculados añadidos para optimizar el listado
    volumenTotal: Optional[Decimal] = Field(0, description="Volumen total de la proforma")
    volumenAsignado: Optional[Decimal] = Field(0, description="Volumen asignado en OCs")
    volumenPendiente: Optional[Decimal] = Field(0, description="Volumen pendiente")
    oc_asociadas: Optional[int] = Field(0, description="Cantidad de OCs asociadas")
    estadoFlujo: Optional[str] = Field('sin-oc', description="Estado del flujo (sin-oc, parcial, completado)")

    # Etiquetas de texto para evitar buscar en mantenedores del frontend
    empresa_nombre: Optional[str] = Field(None, description="Nombre de la empresa")
    moneda_nombre: Optional[str] = Field(None, description="Etiqueta o nombre de la moneda")
    estado_nombre: Optional[str] = Field(None, description="Nombre del estado")
    usuario_nombre: Optional[str] = Field(None, description="Nombre del usuario encargado")
    facturar_a_nombre: Optional[str] = Field(None, description="Nombre del cliente a facturar")
    oe_numero: Optional[str] = Field(None, description="Número de la OE asociada")

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

    detalles: list[ProformaDetalleItemRead] = Field(default_factory=list, description="Detalles de productos de la proforma")
    ordenes_compra: list[ProformaOrdenCompraEmbeddedRead] = Field(default_factory=list, description="Ordenes de compra asociadas")
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
