from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class PackingListDetalleBase(BaseModel):
    oc: Optional[str] = None
    etiqueta: Optional[str] = None
    numero_pqts: Optional[int] = None
    espesor: Optional[Decimal] = None
    ancho: Optional[Decimal] = None
    largo: Optional[Decimal] = None
    piezas: Optional[int] = None
    origen_detalle: Optional[str] = None


class PackingListDetalleCreate(PackingListDetalleBase):
    pass


class PackingListDetalleOut(PackingListDetalleBase):
    id_packing_list_detalle: int

    class Config:
        from_attributes = True


class PackingListGuiaBase(BaseModel):
    guia_despacho: str
    fecha_despacho: date
    orden: int = 0


class PackingListGuiaCreate(PackingListGuiaBase):
    detalles: List[PackingListDetalleCreate] = Field(default_factory=list)


class PackingListGuiaOut(PackingListGuiaBase):
    id_packing_list_guia: int
    detalles: List[PackingListDetalleOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


class PackingListBase(BaseModel):
    origen: Optional[str] = None
    producto: Optional[str] = None
    destino: Optional[str] = None


class PackingListCreate(PackingListBase):
    guias: List[PackingListGuiaCreate] = Field(..., min_length=1)


class PackingListUpdate(PackingListBase):
    guias: List[PackingListGuiaCreate] = Field(..., min_length=1)


class PackingListOut(PackingListBase):
    id_packing_list: int
    orden_compra_id: int
    guias: List[PackingListGuiaOut] = Field(default_factory=list)

    class Config:
        from_attributes = True
