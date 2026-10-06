import os
import math
import shutil
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.db.session import get_db
from app.models.guia_costo_servicio import (
    GuiaCostoServicio,
    GuiaCostoStockPlanta,
    GuiaCostoResumenGeneral,
)
from app.models.orden_servicio import OrdenServicio
from app.models.orden_compra import OrdenCompra
from app.schemas.inventario_segunda import (
    GuiaInventarioSegundaRead,
    PaginatedGuiaInventarioSegundaResponse,
    ItemStockSegunda,
    PaginatedItemInventarioSegundaResponse,
    StatsInventarioSegundaResponse,
    DesgloseOrigenSegunda,
    DesgloseDimensionSegunda,
    DesgloseMensualSegunda,
)

router = APIRouter(prefix="/inventario_segunda", tags=["inventario_segunda"])


def _is_2da_stock(tipo_stock: Optional[str]) -> bool:
    if not tipo_stock:
        return False
    ts = str(tipo_stock).strip().upper()
    return any(k in ts for k in ["2DA", "2ERA", "2°", "2"])


def _is_2da_movimiento(movimiento: Optional[str]) -> bool:
    if not movimiento:
        return False
    m = str(movimiento).strip().upper()
    return any(k in m for k in ["2DA", "2ERA", "2°", "FLEJES 2DA", "FLEJES 2ERA"])


def _guia_has_segunda(guia: GuiaCostoServicio) -> bool:
    if guia.flejes_2da is not None and float(guia.flejes_2da) > 0:
        return True
    if guia.stock_planta and any(_is_2da_stock(sp.tipo_stock) for sp in guia.stock_planta):
        return True
    if guia.resumen_general and any(_is_2da_movimiento(rg.movimiento) for rg in guia.resumen_general):
        return True
    return False


def _format_guia_segunda(guia: GuiaCostoServicio) -> GuiaInventarioSegundaRead:
    stock_2da_items: List[ItemStockSegunda] = []
    if guia.stock_planta:
        for sp in guia.stock_planta:
            if _is_2da_stock(sp.tipo_stock):
                stock_2da_items.append(
                    ItemStockSegunda(
                        id_stock_planta=sp.id_stock_planta,
                        id_guia_costo_servicio=guia.id_guia_costo_servicio,
                        numero_guia=guia.numero_guia,
                        fecha_despacho=guia.fecha_despacho,
                        origen=guia.origen,
                        destino=guia.destino,
                        producto=guia.producto,
                        oc_compra_ref=guia.oc_compra_ref,
                        espesor=float(sp.espesor) if sp.espesor is not None else None,
                        ancho=float(sp.ancho) if sp.ancho is not None else None,
                        largo=float(sp.largo) if sp.largo is not None else None,
                        piezas=sp.piezas,
                        volumen_m3=float(sp.volumen_m3) if sp.volumen_m3 is not None else None,
                        tipo_stock=sp.tipo_stock or "2da",
                    )
                )

    resumen_2da_items = []
    if guia.resumen_general:
        for rg in guia.resumen_general:
            if _is_2da_movimiento(rg.movimiento):
                resumen_2da_items.append(
                    {
                        "id_resumen_general": rg.id_resumen_general,
                        "id_guia_costo_servicio": guia.id_guia_costo_servicio,
                        "oc_tabla": rg.oc_tabla,
                        "movimiento": rg.movimiento,
                        "volumen_m3": float(rg.volumen_m3) if rg.volumen_m3 is not None else None,
                        "estado": rg.estado,
                    }
                )

    # Calculate total volume of 2da
    vol_2da = 0.0
    if stock_2da_items:
        vol_2da = sum(item.volumen_m3 or 0.0 for item in stock_2da_items)
    elif resumen_2da_items:
        vol_2da = sum(item.get("volumen_m3") or 0.0 for item in resumen_2da_items)
    elif guia.flejes_2da is not None:
        vol_2da = float(guia.flejes_2da)

    # Calculate total pieces of 2da
    total_piezas = 0
    if stock_2da_items:
        total_piezas = sum(item.piezas or 0 for item in stock_2da_items)

    os_ids = [os.id_orden_servicio for os in guia.ordenes_servicio] if guia.ordenes_servicio else []
    oc_ids = [oc.id_orden_compra for oc in guia.ordenes_compra] if guia.ordenes_compra else []

    servicios_list = [d.to_dict() for d in guia.detalles] if guia.detalles else []
    proceso_list = [pr.to_dict() for pr in guia.detalles_proceso] if guia.detalles_proceso else []

    return GuiaInventarioSegundaRead(
        id_guia_costo_servicio=guia.id_guia_costo_servicio,
        numero_guia=guia.numero_guia,
        fecha_despacho=guia.fecha_despacho,
        fecha_registro=guia.fecha_registro,
        origen=guia.origen,
        destino=guia.destino,
        producto=guia.producto,
        oc_compra_ref=guia.oc_compra_ref,
        flejes_2da=float(guia.flejes_2da) if guia.flejes_2da is not None else None,
        total_volumen_2da=round(vol_2da, 4),
        total_piezas_2da=total_piezas,
        url_documento=guia.url_documento,
        observaciones=guia.observaciones,
        ordenes_compra_ids=oc_ids,
        ordenes_servicio_ids=os_ids,
        stock_planta_2da=stock_2da_items,
        resumen_general_2da=resumen_2da_items,
        servicios=servicios_list,
        detalles_proceso=proceso_list,
    )


@router.get("/", response_model=PaginatedGuiaInventarioSegundaResponse)
def get_inventario_segunda_guias(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    origen: Optional[str] = Query(None),
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    id_orden_servicio: Optional[int] = Query(None),
    id_orden_compra: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(GuiaCostoServicio)

    if id_orden_servicio and isinstance(id_orden_servicio, int):
        query = query.join(GuiaCostoServicio.ordenes_servicio).filter(
            OrdenServicio.id_orden_servicio == id_orden_servicio
        )

    if id_orden_compra and isinstance(id_orden_compra, int):
        query = query.join(GuiaCostoServicio.ordenes_compra).filter(
            OrdenCompra.id_orden_compra == id_orden_compra
        )

    if origen and isinstance(origen, str):
        query = query.filter(GuiaCostoServicio.origen == origen)

    if fecha_desde and isinstance(fecha_desde, str):
        query = query.filter(GuiaCostoServicio.fecha_despacho >= fecha_desde)
    if fecha_hasta and isinstance(fecha_hasta, str):
        query = query.filter(GuiaCostoServicio.fecha_despacho <= fecha_hasta)

    if search and isinstance(search, str):
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                GuiaCostoServicio.numero_guia.ilike(search_term),
                GuiaCostoServicio.origen.ilike(search_term),
                GuiaCostoServicio.destino.ilike(search_term),
                GuiaCostoServicio.producto.ilike(search_term),
                GuiaCostoServicio.oc_compra_ref.ilike(search_term),
                GuiaCostoServicio.observaciones.ilike(search_term),
            )
        )

    all_guias = query.order_by(desc(GuiaCostoServicio.fecha_despacho), desc(GuiaCostoServicio.id_guia_costo_servicio)).all()
    guias_con_segunda = [g for g in all_guias if _guia_has_segunda(g)]

    total_items = len(guias_con_segunda)
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
    offset = (page - 1) * page_size

    paged_guias = guias_con_segunda[offset : offset + page_size]
    items_read = [_format_guia_segunda(g) for g in paged_guias]

    return {
        "total_items": total_items,
        "total_pages": total_pages,
        "page": page,
        "page_size": page_size,
        "items": items_read,
    }


@router.get("/items", response_model=PaginatedItemInventarioSegundaResponse)
def get_inventario_segunda_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    origen: Optional[str] = Query(None),
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(GuiaCostoServicio)

    if origen and isinstance(origen, str):
        query = query.filter(GuiaCostoServicio.origen == origen)
    if fecha_desde and isinstance(fecha_desde, str):
        query = query.filter(GuiaCostoServicio.fecha_despacho >= fecha_desde)
    if fecha_hasta and isinstance(fecha_hasta, str):
        query = query.filter(GuiaCostoServicio.fecha_despacho <= fecha_hasta)

    all_guias = query.order_by(desc(GuiaCostoServicio.fecha_despacho), desc(GuiaCostoServicio.id_guia_costo_servicio)).all()
    flat_items: List[ItemStockSegunda] = []

    for g in all_guias:
        formatted = _format_guia_segunda(g)
        if formatted.stock_planta_2da:
            for item in formatted.stock_planta_2da:
                flat_items.append(item)
        elif formatted.total_volumen_2da > 0:
            # Fallback item if no stock_planta rows but volume exists
            flat_items.append(
                ItemStockSegunda(
                    id_stock_planta=None,
                    id_guia_costo_servicio=g.id_guia_costo_servicio,
                    numero_guia=g.numero_guia,
                    fecha_despacho=g.fecha_despacho,
                    origen=g.origen,
                    destino=g.destino,
                    producto=g.producto,
                    oc_compra_ref=g.oc_compra_ref,
                    espesor=None,
                    ancho=None,
                    largo=None,
                    piezas=None,
                    volumen_m3=formatted.total_volumen_2da,
                    tipo_stock="2da",
                )
            )

    if search and isinstance(search, str):
        s = search.strip().lower()
        flat_items = [
            it
            for it in flat_items
            if s in (it.numero_guia or "").lower()
            or s in (it.origen or "").lower()
            or s in (it.destino or "").lower()
            or s in (it.producto or "").lower()
            or s in (it.oc_compra_ref or "").lower()
            or (it.espesor and s in str(it.espesor))
            or (it.ancho and s in str(it.ancho))
            or (it.largo and s in str(it.largo))
        ]

    total_items = len(flat_items)
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
    offset = (page - 1) * page_size
    paged_items = flat_items[offset : offset + page_size]

    return {
        "total_items": total_items,
        "total_pages": total_pages,
        "page": page,
        "page_size": page_size,
        "items": paged_items,
    }


@router.get("/stats", response_model=StatsInventarioSegundaResponse)
def get_inventario_segunda_stats(
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    origen: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(GuiaCostoServicio)

    if origen and isinstance(origen, str):
        query = query.filter(GuiaCostoServicio.origen == origen)
    if fecha_desde and isinstance(fecha_desde, str):
        query = query.filter(GuiaCostoServicio.fecha_despacho >= fecha_desde)
    if fecha_hasta and isinstance(fecha_hasta, str):
        query = query.filter(GuiaCostoServicio.fecha_despacho <= fecha_hasta)

    all_guias = query.all()
    guias_segunda = [g for g in all_guias if _guia_has_segunda(g)]

    total_volumen_2da = 0.0
    total_piezas_2da = 0
    origen_map = {}
    dimension_map = {}
    mensual_map = {}

    for g in guias_segunda:
        formatted = _format_guia_segunda(g)
        vol = formatted.total_volumen_2da
        piezas = formatted.total_piezas_2da

        total_volumen_2da += vol
        total_piezas_2da += piezas

        # Por origen
        o_name = g.origen or "Sin Origen"
        if o_name not in origen_map:
            origen_map[o_name] = {"origen": o_name, "total_m3": 0.0, "total_piezas": 0, "guias_count": 0}
        origen_map[o_name]["total_m3"] += vol
        origen_map[o_name]["total_piezas"] += piezas
        origen_map[o_name]["guias_count"] += 1

        # Por mes
        m_key = g.fecha_despacho.strftime("%Y-%m") if g.fecha_despacho else "Sin Fecha"
        if m_key not in mensual_map:
            mensual_map[m_key] = {"mes_anio": m_key, "total_m3": 0.0, "total_piezas": 0, "guias_count": 0}
        mensual_map[m_key]["total_m3"] += vol
        mensual_map[m_key]["total_piezas"] += piezas
        mensual_map[m_key]["guias_count"] += 1

        # Por dimensiones
        if formatted.stock_planta_2da:
            for it in formatted.stock_planta_2da:
                dim_key = f"{it.espesor or '-'} x {it.ancho or '-'} x {it.largo or '-'}"
                if dim_key not in dimension_map:
                    dimension_map[dim_key] = {
                        "dimension": dim_key,
                        "espesor": it.espesor,
                        "ancho": it.ancho,
                        "largo": it.largo,
                        "total_piezas": 0,
                        "total_m3": 0.0,
                    }
                dimension_map[dim_key]["total_piezas"] += (it.piezas or 0)
                dimension_map[dim_key]["total_m3"] += (it.volumen_m3 or 0.0)
        elif vol > 0:
            dim_key = g.producto or "Estándar 2da"
            if dim_key not in dimension_map:
                dimension_map[dim_key] = {
                    "dimension": dim_key,
                    "espesor": None,
                    "ancho": None,
                    "largo": None,
                    "total_piezas": 0,
                    "total_m3": 0.0,
                }
            dimension_map[dim_key]["total_m3"] += vol

    desglose_origen = [
        DesgloseOrigenSegunda(
            origen=d["origen"],
            total_m3=round(d["total_m3"], 4),
            total_piezas=d["total_piezas"],
            guias_count=d["guias_count"],
        )
        for d in origen_map.values()
    ]
    desglose_origen.sort(key=lambda x: x.total_m3, reverse=True)

    desglose_dimension = [
        DesgloseDimensionSegunda(
            dimension=d["dimension"],
            espesor=d["espesor"],
            ancho=d["ancho"],
            largo=d["largo"],
            total_piezas=d["total_piezas"],
            total_m3=round(d["total_m3"], 4),
        )
        for d in dimension_map.values()
    ]
    desglose_dimension.sort(key=lambda x: x.total_m3, reverse=True)

    desglose_mensual = [
        DesgloseMensualSegunda(
            mes_anio=d["mes_anio"],
            total_m3=round(d["total_m3"], 4),
            total_piezas=d["total_piezas"],
            guias_count=d["guias_count"],
        )
        for d in sorted(mensual_map.values(), key=lambda x: x["mes_anio"])
    ]

    return StatsInventarioSegundaResponse(
        total_volumen_2da_m3=round(total_volumen_2da, 4),
        total_piezas_2da=total_piezas_2da,
        total_guias_con_2da=len(guias_segunda),
        total_origenes=len(origen_map),
        desglose_por_origen=desglose_origen,
        desglose_por_dimension=desglose_dimension,
        desglose_mensual=desglose_mensual,
    )


@router.post("/guia/{id_guia_costo_servicio}/documento")
def upload_documento_guia_segunda(
    id_guia_costo_servicio: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    guia = db.query(GuiaCostoServicio).filter(GuiaCostoServicio.id_guia_costo_servicio == id_guia_costo_servicio).first()
    if not guia:
        raise HTTPException(status_code=404, detail="Guía no encontrada.")

    upload_dir = os.path.join(os.getcwd(), "app", "static", "guias_costo_servicio")
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"guia_costo_{guia.numero_guia}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    guia.url_documento = f"/static/guias_costo_servicio/{filename}"
    db.commit()
    db.refresh(guia)

    return {"message": "Documento subido correctamente", "url_documento": guia.url_documento}
