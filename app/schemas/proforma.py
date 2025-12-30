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

    model_config = ConfigDict(from_attributes=True)


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
