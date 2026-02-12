from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from decimal import Decimal


class DetalleProformaCreate(BaseModel):
    id_proforma: int = Field(..., description="ID de la proforma")
    id_producto: Optional[int] = Field(None, description="ID del producto")
    id_unidad_venta: int = Field(..., description="ID de la unidad de venta")
    texto_libre: Optional[str] = Field(None, description="Texto libre", max_length=200)
    espesor: Optional[str] = Field(None, description="Espesor", max_length=20)
    id_unidad_medida_espesor: Optional[int] = Field(None, description="ID unidad de medida del espesor")
    ancho: Optional[str] = Field(None, description="Ancho", max_length=20)
    id_unidad_medida_ancho: Optional[int] = Field(None, description="ID unidad de medida del ancho")
    largo: Optional[str] = Field(None, description="Largo", max_length=20)
    id_unidad_medida_largo: Optional[int] = Field(None, description="ID unidad de medida del largo")
    piezas: Optional[int] = Field(None, description="Número de piezas")
    cantidad: Decimal = Field(..., description="Cantidad")
    precio_unitario: Decimal = Field(..., description="Precio unitario")
    subtotal: Decimal = Field(..., description="Subtotal")
    volumen: Optional[Decimal] = Field(None, description="Volumen")
    volumen_eq: Decimal = Field(..., description="Volumen equivalente")
    precio_eq: Decimal = Field(..., description="Precio equivalente")

    model_config = ConfigDict(json_schema_extra={"examples": [{
        "id_proforma": 1,
        "id_producto": 1,
        "id_unidad_venta": 1,
        "texto_libre": "Descripción adicional",
        "cantidad": "10",
        "precio_unitario": "100.50",
        "subtotal": "1005.00",
        "volumen_eq": "1.234",
        "precio_eq": "100.50"
    }]})


class DetalleProformaRead(BaseModel):
    id_detalle_proforma: int = Field(..., description="ID del detalle de proforma")
    id_proforma: int = Field(..., description="ID de la proforma")
    id_producto: Optional[int] = Field(None, description="ID del producto")
    id_unidad_venta: int = Field(..., description="ID de la unidad de venta")
    texto_libre: Optional[str] = Field(None, description="Texto libre")
    espesor: Optional[str] = Field(None, description="Espesor")
    id_unidad_medida_espesor: Optional[int] = Field(None, description="ID unidad de medida del espesor")
    ancho: Optional[str] = Field(None, description="Ancho")
    id_unidad_medida_ancho: Optional[int] = Field(None, description="ID unidad de medida del ancho")
    largo: Optional[str] = Field(None, description="Largo")
    id_unidad_medida_largo: Optional[int] = Field(None, description="ID unidad de medida del largo")
    piezas: Optional[int] = Field(None, description="Número de piezas")
    cantidad: Decimal = Field(..., description="Cantidad")
    precio_unitario: Decimal = Field(..., description="Precio unitario")
    subtotal: Decimal = Field(..., description="Subtotal")
    volumen: Optional[Decimal] = Field(None, description="Volumen")
    volumen_eq: Decimal = Field(..., description="Volumen equivalente")
    precio_eq: Decimal = Field(..., description="Precio equivalente")

    model_config = ConfigDict(from_attributes=True)


class DetalleProformaUpdate(BaseModel):
    id_producto: Optional[int] = Field(None, description="ID del producto")
    id_unidad_venta: Optional[int] = Field(None, description="ID de la unidad de venta")
    texto_libre: Optional[str] = Field(None, description="Texto libre", max_length=200)
    espesor: Optional[str] = Field(None, description="Espesor", max_length=20)
    id_unidad_medida_espesor: Optional[int] = Field(None, description="ID unidad de medida del espesor")
    ancho: Optional[str] = Field(None, description="Ancho", max_length=20)
    id_unidad_medida_ancho: Optional[int] = Field(None, description="ID unidad de medida del ancho")
    largo: Optional[str] = Field(None, description="Largo", max_length=20)
    id_unidad_medida_largo: Optional[int] = Field(None, description="ID unidad de medida del largo")
    piezas: Optional[int] = Field(None, description="Número de piezas")
    cantidad: Optional[Decimal] = Field(None, description="Cantidad")
    precio_unitario: Optional[Decimal] = Field(None, description="Precio unitario")
    subtotal: Optional[Decimal] = Field(None, description="Subtotal")
    volumen: Optional[Decimal] = Field(None, description="Volumen")
    volumen_eq: Optional[Decimal] = Field(None, description="Volumen equivalente")
    precio_eq: Optional[Decimal] = Field(None, description="Precio equivalente")
    
    model_config = ConfigDict()
