from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class ContactoProformaCreate(BaseModel):
    id_contacto: int = Field(..., description="Descripción de id_contacto")
    id_proforma: int = Field(..., description="Descripción de id_proforma")

    model_config = ConfigDict(json_schema_extra={"examples": [{"id_contacto": 1, "id_proforma": 1}]})


class ContactoProformaRead(BaseModel):
    id_contacto_proforma: int = Field(..., description="Descripción de id_contacto_proforma")
    id_contacto: int = Field(..., description="Descripción de id_contacto")
    id_proforma: int = Field(..., description="Descripción de id_proforma")

    model_config = ConfigDict(from_attributes=True)


class ContactoProformaUpdate(BaseModel):
    id_contacto: Optional[int] = None
    id_proforma: Optional[int] = None

    model_config = ConfigDict()
