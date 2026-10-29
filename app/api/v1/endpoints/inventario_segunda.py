import os
import math
import shutil
import re
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
from app.models.detalle_orden_compra import DetalleOrdenCompra
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


def _get_effective_2da_stock_planta(guia: GuiaCostoServicio) -> List[GuiaCostoStockPlanta]:
    if not guia.stock_planta:
        return []
    explicit_2da = [sp for sp in guia.stock_planta if _is_2da_stock(sp.tipo_stock)]
    if explicit_2da:
        return explicit_2da
    # En el nuevo formato de Excel (ej. guía 10122), el cuadro único de Stock Planta corresponde a 2da
    sum_all_sp = sum(float(sp.volumen_m3 or 0) for sp in guia.stock_planta)
    if sum_all_sp <= 0:
        return []
    f2da = float(guia.flejes_2da or 0)
    sum_rg_2da = sum(
        float(rg.volumen_m3 or 0)
        for rg in (guia.resumen_general or [])
        if _is_2da_movimiento(rg.movimiento)
    )
    tot_1ra = float(guia.total_m3 or 0)
    if (
        (f2da > 0 and abs(sum_all_sp - f2da) < 0.5)
        or (sum_rg_2da > 0 and abs(sum_all_sp - sum_rg_2da) < 0.5)
        or ((f2da > 0 or sum_rg_2da > 0) and tot_1ra > 0 and abs(sum_all_sp - tot_1ra) > 1.0)
    ):
        return list(guia.stock_planta)
    return []


def _guia_has_segunda(guia: GuiaCostoServicio) -> bool:
    if guia.flejes_2da is not None and float(guia.flejes_2da) > 0:
        return True
    if _get_effective_2da_stock_planta(guia):
        return True
    if guia.resumen_general and any(_is_2da_movimiento(rg.movimiento) for rg in guia.resumen_general):
        return True
    return False


def _compute_costos_segunda(guia: GuiaCostoServicio, db: Optional[Session]) -> dict:
    if not db:
        return {
            "resumen_costos": {},
            "total_costo_madera": 0.0,
            "total_servicios": 0.0,
            "total_costo_final": 0.0,
            "costo_promedio_m3": 0.0,
        }

    # 1. Agrupar bloques de resumen general por entrada/salida (Entrada rústico vs Flejes 1ra + Flejes 2da)
    rg_blocks = []
    curr_b = None
    if guia.resumen_general:
        for rg in guia.resumen_general:
            mov = str(rg.movimiento or "").upper()
            v = float(rg.volumen_m3 or 0)
            if "ENTRADA" in mov or "RUSTICO" in mov or curr_b is None:
                curr_b = {
                    "oc": str(rg.oc_tabla or ""),
                    "in": v if ("ENTRADA" in mov or "RUSTICO" in mov) else 0.0,
                    "1ra": 0.0,
                    "2da": 0.0,
                    "rg_items": [rg],
                }
                rg_blocks.append(curr_b)
            else:
                curr_b["rg_items"].append(rg)
                if any(k in mov for k in ["2DA", "2ERA", "2°", "FLEJES 2DA", "FLEJES 2ERA"]):
                    curr_b["2da"] += v
                elif any(k in mov for k in ["TERMINADO", "1RA", "1ERA", "1°", "FLEJES"]):
                    curr_b["1ra"] += v

    rows_2da = [
        rg for rg in (guia.resumen_general or [])
        if any(k in str(rg.movimiento or "").upper() for k in ["2DA", "2ERA", "2°", "FLEJES 2DA", "FLEJES 2ERA"])
    ]

    resumen_costos = {}
    total_costo_madera = 0.0
    total_costo_servicios = 0.0
    total_costo_final = 0.0
    total_vol_2da = 0.0

    for rg in rows_2da:
        vol_rg = float(rg.volumen_m3 or 0)

        # Match bloque primero (en el nuevo formato la columna OC/Tabla solo viene en la fila Entrada rústico del bloque)
        matched_b = None
        for b in rg_blocks:
            if rg in b["rg_items"]:
                matched_b = b
                break

        oc_str = str(rg.oc_tabla or (matched_b["oc"] if matched_b else "") or "")

        cands = [int(n) for n in re.findall(r"\d+", oc_str)]
        if 8059 in cands and 8057 not in cands:
            cands.append(8057)
        if 8058 in cands and 8057 not in cands:
            cands.append(8057)
        if not cands and guia.ordenes_compra:
            cands = [oc.id_orden_compra for oc in guia.ordenes_compra]

        is_sd = "SD" in oc_str.upper()
        is_bs = "BS" in oc_str.upper()
        if not matched_b:
            for b in rg_blocks:
                b_oc = b["oc"]
                if any(str(cid) in b_oc for cid in cands):
                    b_sd = "SD" in b_oc.upper()
                    b_bs = "BS" in b_oc.upper()
                    if (is_sd and b_sd) or (is_bs and b_bs) or (not is_sd and not is_bs and not b_sd and not b_bs):
                        matched_b = b
                        break

        # Match detalle proceso (puede haber múltiples líneas para la misma OC, ej. distintas escuadrías)
        matched_dps = []
        if guia.detalles_proceso:
            exact_dps = []
            fallback_dps = []
            for dp in guia.detalles_proceso:
                dp_oc = str(dp.oc_compra_entrada or "")
                if any(str(cid) in dp_oc for cid in cands):
                    dp_sd = "SD" in dp_oc.upper()
                    dp_bs = "BS" in dp_oc.upper()
                    if (is_sd and dp_sd) or (is_bs and dp_bs) or (not is_sd and not is_bs and not dp_sd and not dp_bs):
                        exact_dps.append(dp)
                    else:
                        fallback_dps.append(dp)
            matched_dps = exact_dps if exact_dps else fallback_dps
            if not matched_dps and len(guia.detalles_proceso) == 1:
                matched_dps = [guia.detalles_proceso[0]]
        matched_dp = matched_dps[0] if matched_dps else None
        sum_dp_in = sum(float(d.volumen_m3_entrada or 0) for d in matched_dps)
        sum_dp_out = sum(float(d.volumen_m3_salida or 0) for d in matched_dps)

        # Calcular volumen de entrada y salida para rendimiento
        vol_in = 1.0
        vol_out = 1.0
        if matched_b and (matched_b["1ra"] + matched_b["2da"]) > 0:
            if matched_b["in"] > 0:
                vol_in = matched_b["in"]
                vol_out = matched_b["1ra"] + matched_b["2da"]
            else:
                dp_vol_cand = sum_dp_in if sum_dp_in > 0 else sum_dp_out
                sum_salida = matched_b["1ra"] + matched_b["2da"]
                if dp_vol_cand > 0 and sum_salida > 0:
                    vol_in = dp_vol_cand
                    vol_out = sum_salida
                else:
                    vol_in = 1.0
                    vol_out = 1.0
        elif sum_dp_in > 0:
            vol_in = sum_dp_in
            if sum_dp_out > 0:
                vol_out = sum_dp_out

        # Precio madera desde DetalleOrdenCompra
        orig_dets = db.query(DetalleOrdenCompra).filter(DetalleOrdenCompra.id_orden_compra.in_(cands)).all() if cands else []
        d_match = None
        if is_sd and orig_dets:
            d_match = max(orig_dets, key=lambda d: float(d.precio_eq or d.precio_unitario or 0))
        elif is_bs and orig_dets:
            d_match = min(orig_dets, key=lambda d: float(d.precio_eq or d.precio_unitario or 0))
        elif orig_dets:
            d_match = orig_dets[0]

        comision = round(float(getattr(d_match, "comision", 0) or 0.0), 2) if d_match else 0.0
        flete = round(float(getattr(d_match, "flete", 0) or 0.0), 2) if d_match else 0.0
        pu = float(d_match.precio_eq or d_match.precio_unitario or 0) if d_match else 0.0
        costo_compra = pu + comision + flete

        costo_madera_m3 = round((vol_in * costo_compra) / vol_out, 2) if vol_out > 0 else round(costo_compra, 2)

        # Servicios Planta ajustados por rendimiento
        servicios_m3 = 0.0
        if guia.detalles:
            tiene_cepillado = False
            dp_in = sum_dp_in
            dp_out = sum_dp_out
            if matched_dps:
                for dp_item in matched_dps:
                    e_in = float(dp_item.espesor_entrada or 0)
                    a_in = float(dp_item.ancho_entrada or 0)
                    e_out = float(dp_item.espesor_salida or 0)
                    a_out = float(dp_item.ancho_salida or 0)
                    if (e_in > e_out + 0.5) or (a_in > a_out + 0.5):
                        tiene_cepillado = True
                        break
            elif matched_b and matched_b.get("in", 0) > 0:
                tiene_cepillado = True

            trozado_det = None
            cepillado_det = None
            for d in guia.detalles:
                s_name = str(d.servicio or "").upper()
                if "TROZAD" in s_name:
                    if not trozado_det or float(d.volumen_m3 or 0) > 0:
                        trozado_det = d
                elif "CEPILLAD" in s_name:
                    cepillado_det = d

            serv_item = 0.0
            if trozado_det and trozado_det.tarifa_usd_m3:
                t_troz = float(trozado_det.tarifa_usd_m3)
                v_troz_in = dp_out if tiene_cepillado else (dp_in or vol_out)
                ratio_troz = (v_troz_in / vol_out) if (v_troz_in > 0 and vol_out > 0) else 1.0
                serv_item += (t_troz * ratio_troz)

            if tiene_cepillado and cepillado_det and cepillado_det.tarifa_usd_m3:
                t_cep = float(cepillado_det.tarifa_usd_m3)
                v_cep_in = dp_in if dp_in > 0 else vol_out
                ratio_cep = (v_cep_in / vol_out) if (v_cep_in > 0 and vol_out > 0) else 1.0
                serv_item += (t_cep * ratio_cep)

            servicios_m3 = round(serv_item, 2)

        costo_unit = round(costo_madera_m3 + servicios_m3, 2)
        costo_mad_tot = round(vol_rg * costo_madera_m3, 2)
        costo_serv_tot = round(vol_rg * servicios_m3, 2)
        costo_tot = round(vol_rg * costo_unit, 2)

        total_costo_madera += costo_mad_tot
        total_costo_servicios += costo_serv_tot
        total_costo_final += costo_tot
        total_vol_2da += vol_rg

        resumen_costos[rg.id_resumen_general] = {
            "oc_tabla": oc_str or None,
            "costo_madera_m3": costo_madera_m3,
            "servicios_m3": servicios_m3,
            "costo_final_unitario": costo_unit,
            "costo_madera_total": costo_mad_tot,
            "costo_servicios_total": costo_serv_tot,
            "costo_final_total": costo_tot,
        }

    # Fallback si no hay filas 2da en resumen general pero sí volumen de 2da en la guía
    if not rows_2da:
        v_fallback = float(guia.flejes_2da or 0)
        eff_sp_2da = _get_effective_2da_stock_planta(guia)
        if v_fallback <= 0 and eff_sp_2da:
            v_fallback = sum(float(sp.volumen_m3 or 0) for sp in eff_sp_2da)
        if v_fallback > 0:
            cands = []
            if guia.oc_compra_ref:
                cands = [int(n) for n in re.findall(r"\d+", guia.oc_compra_ref)]
            if not cands and guia.ordenes_compra:
                cands = [oc.id_orden_compra for oc in guia.ordenes_compra]
            orig_dets = db.query(DetalleOrdenCompra).filter(DetalleOrdenCompra.id_orden_compra.in_(cands)).all() if cands else []
            d_match = orig_dets[0] if orig_dets else None
            pu = float(d_match.precio_eq or d_match.precio_unitario or 0) if d_match else 0.0
            comision = round(float(getattr(d_match, "comision", 0) or 0.0), 2) if d_match else 0.0
            flete = round(float(getattr(d_match, "flete", 0) or 0.0), 2) if d_match else 0.0
            costo_compra = pu + comision + flete

            tot_serv = float(guia.total_usd or 0)
            if not tot_serv and guia.detalles:
                tot_serv = sum(float(d.total_usd or 0) for d in guia.detalles)
            tot_salida = float(guia.total_m3 or 0) + v_fallback
            serv_m3 = round(tot_serv / tot_salida, 2) if tot_salida > 0 else 0.0

            costo_unit = round(costo_compra + serv_m3, 2)
            total_costo_madera = round(v_fallback * costo_compra, 2)
            total_costo_servicios = round(v_fallback * serv_m3, 2)
            total_costo_final = round(v_fallback * costo_unit, 2)
            total_vol_2da = v_fallback

    costo_promedio_m3 = round(total_costo_final / total_vol_2da, 2) if total_vol_2da > 0 else 0.0

    return {
        "resumen_costos": resumen_costos,
        "total_costo_madera": round(total_costo_madera, 2),
        "total_servicios": round(total_costo_servicios, 2),
        "total_costo_final": round(total_costo_final, 2),
        "costo_promedio_m3": costo_promedio_m3,
    }


def _format_guia_segunda(guia: GuiaCostoServicio, db: Optional[Session] = None) -> GuiaInventarioSegundaRead:
    costos_info = _compute_costos_segunda(guia, db) if db else {
        "resumen_costos": {},
        "total_costo_madera": 0.0,
        "total_servicios": 0.0,
        "total_costo_final": 0.0,
        "costo_promedio_m3": 0.0,
    }
    resumen_costos = costos_info["resumen_costos"]
    total_costo_madera = costos_info["total_costo_madera"]
    total_servicios = costos_info["total_servicios"]
    total_costo_final = costos_info["total_costo_final"]
    costo_promedio_m3 = costos_info["costo_promedio_m3"]

    stock_2da_items: List[ItemStockSegunda] = []
    eff_stock_2da = _get_effective_2da_stock_planta(guia)
    if eff_stock_2da:
        vol_2da_stock = sum(float(s.volumen_m3 or 0) for s in eff_stock_2da)
        for sp in eff_stock_2da:
            sp_vol = float(sp.volumen_m3) if sp.volumen_m3 is not None else 0.0
            costo_mad = round(total_costo_madera / vol_2da_stock, 2) if vol_2da_stock > 0 else None
            costo_serv = round(total_servicios / vol_2da_stock, 2) if vol_2da_stock > 0 else None
            c_unit = costo_promedio_m3 if costo_promedio_m3 > 0 else None
            c_tot = round(sp_vol * costo_promedio_m3, 2) if costo_promedio_m3 > 0 else None

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
                    volumen_m3=sp_vol,
                    tipo_stock="2da",
                    costo_madera_m3=costo_mad,
                    servicios_m3=costo_serv,
                    costo_final_unitario=c_unit,
                    costo_final_total=c_tot,
                )
            )

    resumen_2da_items = []
    if guia.resumen_general:
        last_oc_tabla = None
        for rg in guia.resumen_general:
            if rg.oc_tabla and str(rg.oc_tabla).strip():
                last_oc_tabla = str(rg.oc_tabla).strip()
            if _is_2da_movimiento(rg.movimiento):
                c_dict = resumen_costos.get(rg.id_resumen_general, {})
                resumen_2da_items.append(
                    {
                        "id_resumen_general": rg.id_resumen_general,
                        "id_guia_costo_servicio": guia.id_guia_costo_servicio,
                        "oc_tabla": rg.oc_tabla or c_dict.get("oc_tabla") or last_oc_tabla,
                        "movimiento": rg.movimiento,
                        "volumen_m3": float(rg.volumen_m3) if rg.volumen_m3 is not None else None,
                        "estado": rg.estado,
                        "costo_madera_m3": c_dict.get("costo_madera_m3"),
                        "servicios_m3": c_dict.get("servicios_m3"),
                        "costo_final_unitario": c_dict.get("costo_final_unitario"),
                        "costo_madera_total": c_dict.get("costo_madera_total"),
                        "costo_servicios_total": c_dict.get("costo_servicios_total"),
                        "costo_final_total": c_dict.get("costo_final_total"),
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
        total_costo_madera_2da=total_costo_madera,
        total_servicios_2da=total_servicios,
        total_costo_final_2da=total_costo_final,
        costo_promedio_2da_m3=costo_promedio_m3,
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
    items_read = [_format_guia_segunda(g, db) for g in paged_guias]

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
        formatted = _format_guia_segunda(g, db)
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
                    costo_madera_m3=round(formatted.total_costo_madera_2da / formatted.total_volumen_2da, 2) if formatted.total_volumen_2da > 0 else 0.0,
                    servicios_m3=round(formatted.total_servicios_2da / formatted.total_volumen_2da, 2) if formatted.total_volumen_2da > 0 else 0.0,
                    costo_final_unitario=formatted.costo_promedio_2da_m3,
                    costo_final_total=formatted.total_costo_final_2da,
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
    total_costo_final_2da = 0.0
    origen_map = {}
    dimension_map = {}
    mensual_map = {}

    for g in guias_segunda:
        formatted = _format_guia_segunda(g, db)
        vol = formatted.total_volumen_2da
        piezas = formatted.total_piezas_2da
        costo_tot = formatted.total_costo_final_2da

        total_volumen_2da += vol
        total_piezas_2da += piezas
        total_costo_final_2da += costo_tot

        # Por origen
        o_name = g.origen or "Sin Origen"
        if o_name not in origen_map:
            origen_map[o_name] = {"origen": o_name, "total_m3": 0.0, "total_piezas": 0, "guias_count": 0, "total_costo_usd": 0.0}
        origen_map[o_name]["total_m3"] += vol
        origen_map[o_name]["total_piezas"] += piezas
        origen_map[o_name]["guias_count"] += 1
        origen_map[o_name]["total_costo_usd"] += costo_tot

        # Por mes
        m_key = g.fecha_despacho.strftime("%Y-%m") if g.fecha_despacho else "Sin Fecha"
        if m_key not in mensual_map:
            mensual_map[m_key] = {"mes_anio": m_key, "total_m3": 0.0, "total_piezas": 0, "guias_count": 0, "total_costo_usd": 0.0}
        mensual_map[m_key]["total_m3"] += vol
        mensual_map[m_key]["total_piezas"] += piezas
        mensual_map[m_key]["guias_count"] += 1
        mensual_map[m_key]["total_costo_usd"] += costo_tot

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
                        "total_costo_usd": 0.0,
                    }
                dimension_map[dim_key]["total_piezas"] += (it.piezas or 0)
                dimension_map[dim_key]["total_m3"] += (it.volumen_m3 or 0.0)
                dimension_map[dim_key]["total_costo_usd"] += (it.costo_final_total or 0.0)
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
                    "total_costo_usd": 0.0,
                }
            dimension_map[dim_key]["total_m3"] += vol
            dimension_map[dim_key]["total_costo_usd"] += costo_tot

    desglose_origen = [
        DesgloseOrigenSegunda(
            origen=d["origen"],
            total_m3=round(d["total_m3"], 4),
            total_piezas=d["total_piezas"],
            guias_count=d["guias_count"],
            total_costo_usd=round(d["total_costo_usd"], 2),
            costo_promedio_m3=round(d["total_costo_usd"] / d["total_m3"], 2) if d["total_m3"] > 0 else 0.0,
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
            total_costo_usd=round(d["total_costo_usd"], 2),
            costo_promedio_m3=round(d["total_costo_usd"] / d["total_m3"], 2) if d["total_m3"] > 0 else 0.0,
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
            total_costo_usd=round(d["total_costo_usd"], 2),
            costo_promedio_m3=round(d["total_costo_usd"] / d["total_m3"], 2) if d["total_m3"] > 0 else 0.0,
        )
        for d in sorted(mensual_map.values(), key=lambda x: x["mes_anio"])
    ]

    costo_promedio_global = round(total_costo_final_2da / total_volumen_2da, 2) if total_volumen_2da > 0 else 0.0

    return StatsInventarioSegundaResponse(
        total_volumen_2da_m3=round(total_volumen_2da, 4),
        total_piezas_2da=total_piezas_2da,
        total_guias_con_2da=len(guias_segunda),
        total_origenes=len(origen_map),
        total_costo_final_2da=round(total_costo_final_2da, 2),
        costo_promedio_2da_m3=costo_promedio_global,
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
