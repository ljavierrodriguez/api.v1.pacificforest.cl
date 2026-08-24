from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.api.v1.endpoints.inventario_transitorio import get_resumen_inventario_transitorio
from app.api.v1.endpoints.inventario_puerto import get_resumen_inventario_puerto

router = APIRouter(prefix="/inventario", tags=["inventario_dashboard"])


@router.get(
    "/resumen_general",
    summary="GET Resumen General de Inventario (Transitorio + Puerto)",
    description="Obtener un resumen consolidado de los métricas de volumen, costo y distribución para transitorio y puerto."
)
def get_resumen_general_inventario(
    id_bodega: Optional[int] = Query(None, description="Filtrar por ID de bodega"),
    db: Session = Depends(get_db),
):
    resumen_trans = get_resumen_inventario_transitorio(id_bodega=id_bodega, db=db)
    resumen_puerto = get_resumen_inventario_puerto(id_bodega=id_bodega, db=db)

    gran_total_volumen = round(resumen_trans["total_volumen"] + resumen_puerto["total_volumen"], 3)
    gran_total_volumen_eq = round(resumen_trans["total_volumen_eq"] + resumen_puerto["total_volumen_eq"], 3)
    gran_total_costo = round(resumen_trans["total_costo"] + resumen_puerto["total_costo"], 2)
    gran_total_items = resumen_trans["total_items"] + resumen_puerto["total_items"]
    gran_total_paquetes = resumen_trans["total_paquetes"] + resumen_puerto["total_paquetes"]

    return {
        "gran_total": {
            "total_volumen": gran_total_volumen,
            "total_volumen_eq": gran_total_volumen_eq,
            "total_costo": gran_total_costo,
            "total_items": gran_total_items,
            "total_paquetes": gran_total_paquetes,
        },
        "transitorio": resumen_trans,
        "puerto": resumen_puerto,
    }
