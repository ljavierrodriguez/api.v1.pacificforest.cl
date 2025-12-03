from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class DocumentoIdeCreate(BaseModel):
    id_ide: Optional[int] = None
    descripcion: str = Field(..., description="Descripción de descripcion")
    nombre_original: Optional[str] = None
    nombre_archivo: Optional[str] = None
    enviado: Optional[bool] = False

    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "id_ide": 1,
                "descripcion": "Documento de soporte",
                "nombre_original": "soporte.pdf",
                "nombre_archivo": "upload_1234.pdf",
                "enviado": False,
            }
        ]
    })


class DocumentoIdeRead(BaseModel):
    id_documento_ide: int = Field(..., description="Descripción de id_documento_ide")
    id_ide: Optional[int] = None
    descripcion: str = Field(..., description="Descripción de descripcion")
    nombre_original: Optional[str] = None
    nombre_archivo: Optional[str] = None
    enviado: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class DocumentoIdeUpdate(BaseModel):
    id_ide: Optional[int] = None
    descripcion: Optional[str] = None
    nombre_original: Optional[str] = None
    nombre_archivo: Optional[str] = None
    enviado: Optional[bool] = None

    model_config = ConfigDict()
