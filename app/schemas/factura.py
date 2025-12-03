from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class FacturaBase(BaseModel):
    fecha_creacion: date = Field(..., description="Descripción de fecha_creacion")
    fecha_emision: date = Field(..., description="Descripción de fecha_emision")
    folio_sii: int = Field(..., description="Descripción de folio_sii")
    terms: str = Field(..., description="Descripción de terms")
    carta_credito: Optional[str] = None
    fecha_carta_credito: Optional[str] = None
    id_ide: int = Field(..., description="Descripción de id_ide")
    subtotal: Optional[str] = None
    total: Optional[str] = None
    descuento: Optional[str] = None
    contract: Optional[str] = None
    nota: Optional[str] = None
    nota_al_pie: Optional[str] = None


class FacturaCreate(FacturaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "fecha_creacion": "2025-12-01",
                    "fecha_emision": "2025-12-01",
                    "folio_sii": 12345,
                    "terms": "FOB",
                    "id_ide": 1,
                }
            ]
        }
    )


class FacturaRead(FacturaBase):
    id_factura: int

    model_config = ConfigDict(from_attributes=True)


class FacturaUpdate(FacturaBase):
    terms: Optional[str]
