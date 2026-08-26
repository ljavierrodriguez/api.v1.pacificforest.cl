import math
from decimal import Decimal
from typing import Optional, List, Union
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.db.session import get_db
from app.models.guia_costo_servicio import (
    GuiaCostoServicio,
    DetalleCostoServicio,
    GuiaCostoProductoTerminado,
    GuiaCostoDetalleProceso,
    guia_costo_servicio_os,
    guia_costo_servicio_oc,
)
from app.models.orden_servicio import OrdenServicio
from app.models.orden_compra import OrdenCompra
from app.schemas.guia_costo_servicio import (
    GuiaCostoServicioCreate,
    BatchGuiaCostoServicioCreate,
    GuiaCostoServicioRead,
    PaginatedGuiaCostoServicioResponse,
)

router = APIRouter()


@router.get("/", response_model=PaginatedGuiaCostoServicioResponse)
def get_guias_costo_servicio(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    id_orden_servicio: Optional[int] = Query(None),
    id_orden_compra: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(GuiaCostoServicio)

    if id_orden_servicio:
        query = query.join(GuiaCostoServicio.ordenes_servicio).filter(
            OrdenServicio.id_orden_servicio == id_orden_servicio
        )

    if id_orden_compra:
        query = query.join(GuiaCostoServicio.ordenes_compra).filter(
            OrdenCompra.id_orden_compra == id_orden_compra
        )

    if search:
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

    query = query.order_by(desc(GuiaCostoServicio.id_guia_costo_servicio))

    total_items = query.count()
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
    offset = (page - 1) * page_size

    guias = query.offset(offset).limit(page_size).all()
    items_read = [g.to_dict() for g in guias]

    return {
        "total_items": total_items,
        "total_pages": total_pages,
        "page": page,
        "page_size": page_size,
        "items": items_read,
    }


@router.post("/", response_model=List[GuiaCostoServicioRead], status_code=status.HTTP_201_CREATED)
def create_guia_costo_servicio(
    payload: Union[GuiaCostoServicioCreate, BatchGuiaCostoServicioCreate, List[GuiaCostoServicioCreate]],
    db: Session = Depends(get_db),
):
    if isinstance(payload, BatchGuiaCostoServicioCreate):
        items_to_create = payload.guias
    elif isinstance(payload, list):
        items_to_create = payload
    else:
        items_to_create = [payload]

    if not items_to_create:
        raise HTTPException(status_code=400, detail="No se proporcionaron guías para registrar.")

    created_objs = []

    for item in items_to_create:
        calc_total_usd = Decimal(0)
        detalles_objs = []

        if item.detalles:
            for d in item.detalles:
                det_obj = DetalleCostoServicio(
                    servicio=d.servicio,
                    volumen_m3=d.volumen_m3,
                    tarifa_usd_m3=d.tarifa_usd_m3,
                    total_usd=d.total_usd,
                )
                detalles_objs.append(det_obj)
                if d.total_usd is not None:
                    calc_total_usd += d.total_usd

        prod_term_objs = []
        if item.productos_terminados:
            for pt in item.productos_terminados:
                pt_obj = GuiaCostoProductoTerminado(
                    espesor=pt.espesor,
                    ancho=pt.ancho,
                    largo=pt.largo,
                    piezas=pt.piezas,
                    volumen_m3=pt.volumen_m3,
                )
                prod_term_objs.append(pt_obj)

        proceso_objs = []
        if item.detalles_proceso:
            for dp in item.detalles_proceso:
                dp_obj = GuiaCostoDetalleProceso(
                    origen_entrada=dp.origen_entrada,
                    estado_entrada=dp.estado_entrada,
                    planta_secado=dp.planta_secado,
                    planta_cepillado=dp.planta_cepillado,
                    oc_compra_entrada=dp.oc_compra_entrada,
                    espesor_entrada=dp.espesor_entrada,
                    ancho_entrada=dp.ancho_entrada,
                    largo_entrada=dp.largo_entrada,
                    piezas_entrada=dp.piezas_entrada,
                    volumen_m3_entrada=dp.volumen_m3_entrada,
                    espesor_salida=dp.espesor_salida,
                    ancho_salida=dp.ancho_salida,
                    largo_salida=dp.largo_salida,
                    piezas_salida=dp.piezas_salida,
                    volumen_m3_salida=dp.volumen_m3_salida,
                    proceso=dp.proceso,
                )
                proceso_objs.append(dp_obj)

        final_total_usd = item.total_usd if item.total_usd is not None else calc_total_usd

        guia_obj = GuiaCostoServicio(
            numero_guia=item.numero_guia,
            fecha_despacho=item.fecha_despacho,
            origen=item.origen,
            producto=item.producto,
            destino=item.destino,
            oc_compra_ref=item.oc_compra_ref,
            total_m3=item.total_m3,
            total_usd=final_total_usd,
            observaciones=item.observaciones,
            url_documento=item.url_documento,
            detalles=detalles_objs,
            productos_terminados=prod_term_objs,
            detalles_proceso=proceso_objs,
        )

        # Link OS
        if item.ordenes_servicio_ids:
            os_records = db.query(OrdenServicio).filter(OrdenServicio.id_orden_servicio.in_(item.ordenes_servicio_ids)).all()
            guia_obj.ordenes_servicio.extend(os_records)

        # Link OC
        if item.ordenes_compra_ids:
            oc_records = db.query(OrdenCompra).filter(OrdenCompra.id_orden_compra.in_(item.ordenes_compra_ids)).all()
            guia_obj.ordenes_compra.extend(oc_records)

        db.add(guia_obj)
        created_objs.append(guia_obj)

    db.commit()
    for g in created_objs:
        db.refresh(g)

    return [g.to_dict() for g in created_objs]


@router.get("/stats/summary")
def get_guia_costo_servicio_stats(
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    origen: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(GuiaCostoServicio)

    if fecha_desde:
        query = query.filter(GuiaCostoServicio.fecha_despacho >= fecha_desde)
    if fecha_hasta:
        query = query.filter(GuiaCostoServicio.fecha_despacho <= fecha_hasta)
    if origen:
        query = query.filter(GuiaCostoServicio.origen == origen)

    guias = query.all()

    total_guias_count = len(guias)
    
    # Calculate exact cost sum from details (or header if empty)
    total_costo_usd = 0.0
    for g in guias:
        if g.detalles:
            total_costo_usd += sum(float(d.total_usd or 0) for d in g.detalles)
        else:
            total_costo_usd += float(g.total_usd or 0)

    total_volumen_m3 = sum(float(g.total_m3 or 0) for g in guias)

    # Desglose por Servicio
    servicios_map = {}
    # Desglose por Origen
    origen_map = {}
    # Desglose Mensual
    mensual_map = {}

    for g in guias:
        g_cost = sum(float(d.total_usd or 0) for d in g.detalles) if g.detalles else float(g.total_usd or 0)
        
        o_name = g.origen or "Sin Origen"
        if o_name not in origen_map:
            origen_map[o_name] = {"origen": o_name, "total_usd": 0.0, "total_m3": 0.0, "guias_count": 0}
        origen_map[o_name]["total_usd"] += g_cost
        origen_map[o_name]["total_m3"] += float(g.total_m3 or 0)
        origen_map[o_name]["guias_count"] += 1

        m_key = g.fecha_despacho.strftime("%Y-%m") if g.fecha_despacho else "Sin Fecha"
        if m_key not in mensual_map:
            mensual_map[m_key] = {"mes_anio": m_key, "total_usd": 0.0, "total_m3": 0.0, "guias_count": 0}
        mensual_map[m_key]["total_usd"] += g_cost
        mensual_map[m_key]["total_m3"] += float(g.total_m3 or 0)
        mensual_map[m_key]["guias_count"] += 1

        if g.detalles:
            for d in g.detalles:
                s_name = d.servicio.strip() if d.servicio else "Otro Servicio"
                if s_name not in servicios_map:
                    servicios_map[s_name] = {
                        "servicio": s_name,
                        "total_usd": 0.0,
                        "total_m3": 0.0,
                        "tarifa_promedio_usd_m3": 0.0,
                        "cantidad_registros": 0,
                    }
                servicios_map[s_name]["total_usd"] += float(d.total_usd or 0)
                servicios_map[s_name]["total_m3"] += float(d.volumen_m3 or 0)
                servicios_map[s_name]["cantidad_registros"] += 1

    total_volumen_servicios_m3 = sum(s_data["total_m3"] for s_data in servicios_map.values())

    desglose_servicios = []
    for s_name, s_data in servicios_map.items():
        vol = s_data["total_m3"]
        cost = s_data["total_usd"]
        s_data["total_usd"] = round(cost, 2)
        s_data["total_m3"] = round(vol, 4)
        s_data["tarifa_promedio_usd_m3"] = round(cost / vol, 2) if vol > 0 else 0.0
        desglose_servicios.append(s_data)

    desglose_servicios.sort(key=lambda x: x["total_usd"], reverse=True)

    desglose_origen = []
    for o_name, o_data in origen_map.items():
        o_data["total_usd"] = round(o_data["total_usd"], 2)
        o_data["total_m3"] = round(o_data["total_m3"], 4)
        desglose_origen.append(o_data)

    desglose_origen.sort(key=lambda x: x["total_usd"], reverse=True)

    desglose_mensual = []
    for m_key, m_data in sorted(mensual_map.items()):
        m_data["total_usd"] = round(m_data["total_usd"], 2)
        m_data["total_m3"] = round(m_data["total_m3"], 4)
        desglose_mensual.append(m_data)

    tarifa_promedio_usd_m3 = round(total_costo_usd / total_volumen_m3, 2) if total_volumen_m3 > 0 else 0.0
    tarifa_promedio_servicio_usd_m3 = round(total_costo_usd / total_volumen_servicios_m3, 2) if total_volumen_servicios_m3 > 0 else 0.0

    return {
        "total_costo_usd": round(total_costo_usd, 2),
        "total_volumen_m3": round(total_volumen_m3, 4),
        "total_volumen_servicios_m3": round(total_volumen_servicios_m3, 4),
        "tarifa_promedio_usd_m3": tarifa_promedio_usd_m3,
        "tarifa_promedio_servicio_usd_m3": tarifa_promedio_servicio_usd_m3,
        "total_guias_count": total_guias_count,
        "desglose_servicios": desglose_servicios,
        "desglose_origen": desglose_origen,
        "desglose_mensual": desglose_mensual,
    }


@router.get("/{id_guia_costo_servicio}", response_model=GuiaCostoServicioRead)
def get_guia_costo_servicio_by_id(
    id_guia_costo_servicio: int,
    db: Session = Depends(get_db),
):
    guia = db.query(GuiaCostoServicio).filter(GuiaCostoServicio.id_guia_costo_servicio == id_guia_costo_servicio).first()
    if not guia:
        raise HTTPException(status_code=444, detail="Guía de costo de servicio no encontrada.")
    return guia.to_dict()


@router.delete("/all/bulk-delete", status_code=status.HTTP_200_OK)
def delete_all_guias_costo_servicio(
    db: Session = Depends(get_db),
):
    guias = db.query(GuiaCostoServicio).all()
    count = len(guias)
    for g in guias:
        db.delete(g)
    db.commit()
    return {"message": f"Se eliminaron {count} guías de costo de servicio correctamente.", "deleted_count": count}


@router.delete("/{id_guia_costo_servicio}", status_code=status.HTTP_200_OK)
def delete_guia_costo_servicio(
    id_guia_costo_servicio: int,
    db: Session = Depends(get_db),
):
    guia = db.query(GuiaCostoServicio).filter(GuiaCostoServicio.id_guia_costo_servicio == id_guia_costo_servicio).first()
    if not guia:
        raise HTTPException(status_code=404, detail="Guía de costo de servicio no encontrada.")

    db.delete(guia)
    db.commit()
    return {"message": "Guía de costo de servicio eliminada correctamente."}
