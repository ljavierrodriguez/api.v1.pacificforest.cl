from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date


class OperacionExportacionCreate(BaseModel):
    facturar_a: int = Field(..., description="ID del cliente al que se factura")
    consignar_a: int = Field(..., description="ID del cliente al que se consigna")
    notificar_a: int = Field(..., description="ID del cliente al que se notifica")
    id_puerto_origen: int = Field(..., description="ID del puerto de origen")
    id_puerto_destino: Optional[int] = Field(None, description="ID del puerto de destino")
    id_forma_pago: int = Field(..., description="ID de la forma de pago")
    id_estado_oe: int = Field(..., description="ID del estado de la operación")
    fecha: date = Field(..., description="Fecha de la operación")

    model_config = ConfigDict(json_schema_extra={
        "examples": [{
            "facturar_a": 1,
            "consignar_a": 1,
            "notificar_a": 1,
            "id_puerto_origen": 1,
            "id_puerto_destino": 2,
            "id_forma_pago": 1,
            "id_estado_oe": 1,
            "fecha": "2025-12-01"
        }]
    })


class OperacionExportacionRead(BaseModel):
    id_operacion_exportacion: int = Field(..., description="ID único de la operación de exportación")
    facturar_a: int = Field(..., description="ID del cliente al que se factura")
    consignar_a: int = Field(..., description="ID del cliente al que se consigna")
    notificar_a: int = Field(..., description="ID del cliente al que se notifica")
    id_puerto_origen: Optional[int] = Field(None, description="ID del puerto de origen")
    id_puerto_destino: Optional[int] = Field(None, description="ID del puerto de destino")
    id_forma_pago: int = Field(..., description="ID de la forma de pago")
    id_estado_oe: int = Field(..., description="ID del estado de la operación")
    fecha: date = Field(..., description="Fecha de la operación")
    id_proforma: Optional[int] = Field(None, description="ID de la proforma asociada, si existe")

    # Etiquetas de texto para evitar llamadas adicionales desde el frontend
    facturar_a_nombre: Optional[str] = Field(None, description="Razón social del cliente a facturar")
    consignar_a_nombre: Optional[str] = Field(None, description="Razón social del cliente a consignar")
    notificar_a_nombre: Optional[str] = Field(None, description="Razón social del cliente a notificar")
    puerto_origen_nombre: Optional[str] = Field(None, description="Nombre del puerto de origen")
    puerto_destino_nombre: Optional[str] = Field(None, description="Nombre del puerto de destino")
    forma_pago_nombre: Optional[str] = Field(None, description="Nombre de la forma de pago")
    estado_oe_nombre: Optional[str] = Field(None, description="Nombre del estado de la operación")

    model_config = ConfigDict(from_attributes=True)


class OperacionExportacionUpdate(BaseModel):
    facturar_a: Optional[int] = Field(default=None, description="ID del cliente al que se factura")
    consignar_a: Optional[int] = Field(default=None, description="ID del cliente al que se consigna")
    notificar_a: Optional[int] = Field(default=None, description="ID del cliente al que se notifica")
    id_puerto_origen: Optional[int] = Field(default=None, description="ID del puerto de origen")
    id_puerto_destino: Optional[int] = Field(default=None, description="ID del puerto de destino")
    id_forma_pago: Optional[int] = Field(default=None, description="ID de la forma de pago")
    id_estado_oe: Optional[int] = Field(default=None, description="ID del estado de la operación")
    fecha: Optional[date] = Field(default=None, description="Fecha de la operación")
    
    model_config = ConfigDict()
