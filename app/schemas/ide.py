from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class IdeCreate(BaseModel):
    id_proforma: Optional[int] = None
    id_tipo_envase: Optional[int] = None
    referencia: Optional[str] = None
    model_config = ConfigDict(json_schema_extra={"examples": [{"referencia": "IDE-123"}]})


class IdeRead(BaseModel):
    id_ide: int = Field(..., description="Descripción de id_ide")
    id_proforma: Optional[int] = Field(default=None, description="Descripción de id_proforma")
    id_tipo_envase: Optional[int] = Field(default=None, description="Descripción de id_tipo_envase")
    referencia: Optional[str] = Field(default=None, description="Descripción de referencia")
    model_config = ConfigDict(from_attributes=True)


class IdeUpdate(BaseModel):
    referencia: Optional[str] = None
    model_config = ConfigDict()
