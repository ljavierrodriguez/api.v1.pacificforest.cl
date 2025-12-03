from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class DetallePlCreate(BaseModel):
    id_ple: int = Field(..., description="Descripción de id_ple")
    id_plc: Optional[int] = None
    etiqueta: str = Field(..., description="Descripción de etiqueta")
    descripcion: str = Field(..., description="Descripción de descripcion")
    id_unidad_venta: int = Field(..., description="Descripción de id_unidad_venta")
    cantidad: Optional[int] = None
    espesor_ple: str = Field(..., description="Descripción de espesor_ple")
    id_unidad_medida_espesor_ple: int = Field(..., description="Descripción de id_unidad_medida_espesor_ple")
    ancho_ple: str = Field(..., description="Descripción de ancho_ple")
    id_unidad_medida_ancho_ple: int = Field(..., description="Descripción de id_unidad_medida_ancho_ple")
    largo_ple: str = Field(..., description="Descripción de largo_ple")
    id_unidad_medida_largo_ple: int = Field(..., description="Descripción de id_unidad_medida_largo_ple")
    piezas: int = Field(..., description="Descripción de piezas")
    volumen_ple: float = Field(..., description="Descripción de volumen_ple")
    id_estado_detalle_ple: int = Field(..., description="Descripción de id_estado_detalle_ple")
    venta_paquete: float = Field(..., description="Descripción de venta_paquete")

    model_config = ConfigDict(json_schema_extra={"examples": [{"id_ple":1, "etiqueta":"A","descripcion":"Desc","id_unidad_venta":1, "espesor_ple":"10","id_unidad_medida_espesor_ple":1, "ancho_ple":"20","id_unidad_medida_ancho_ple":1, "largo_ple":"30","id_unidad_medida_largo_ple":1, "piezas":1, "volumen_ple":1.0, "id_estado_detalle_ple":1, "venta_paquete":100.0}]})


class DetallePlRead(BaseModel):
    id_detalle_pl: int = Field(..., description="Descripción de id_detalle_pl")
    id_ple: int = Field(..., description="Descripción de id_ple")
    etiqueta: str = Field(..., description="Descripción de etiqueta")
    descripcion: str = Field(..., description="Descripción de descripcion")
    id_unidad_venta: int = Field(..., description="Descripción de id_unidad_venta")
    piezas: int = Field(..., description="Descripción de piezas")
    volumen_ple: float = Field(..., description="Descripción de volumen_ple")

    model_config = ConfigDict(from_attributes=True)


class DetallePlUpdate(BaseModel):
    descripcion: Optional[str] = None
    cantidad: Optional[int] = None
    piezas: Optional[int] = None

    model_config = ConfigDict()
