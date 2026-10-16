import re
from typing import List, Dict, Any, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.inventario_transitorio import InventarioTransitorio
from app.models.guia_costo_servicio import GuiaCostoServicio, GuiaCostoDetalleProceso, GuiaCostoResumenGeneral
from app.models.orden_servicio import OrdenServicio
from app.models.detalle_orden_servicio import DetalleOrdenServicio
from app.models.orden_compra import OrdenCompra


def _dim_eq(v1, v2) -> bool:
    if v1 is None or v2 is None:
        return False
    try:
        return abs(float(str(v1).replace(",", ".")) - float(str(v2).replace(",", "."))) < 0.1
    except Exception:
        return str(v1).strip().lower() == str(v2).strip().lower()


def get_all_service_entrances(db: Session) -> List[Dict[str, Any]]:
    """
    Obtiene todas las entradas a servicio registradas en el sistema:
    1. Guías de Costo de Servicio (detalles_proceso y resumen_general)
    2. Órdenes de Servicio (detalle_orden_servicio)
    """
    entrances: List[Dict[str, Any]] = []

    # 1. Guías de Costo de Servicio
    guias_cs = db.query(GuiaCostoServicio).all()
    for g in guias_cs:
        has_dp = False
        if g.detalles_proceso:
            for dp in g.detalles_proceso:
                vol_in = float(dp.volumen_m3_entrada or 0)
                pzs_in = float(dp.piezas_entrada or 0)
                if vol_in > 0 or pzs_in > 0:
                    has_dp = True
                    # Extraer OCs candidatas
                    primary_oc_ids: List[int] = []
                    if dp.oc_compra_entrada:
                        primary_oc_ids.extend([int(n) for n in re.findall(r"\d+", str(dp.oc_compra_entrada))])

                    fallback_oc_ids: List[int] = list(primary_oc_ids)
                    if g.ordenes_compra:
                        for oc in g.ordenes_compra:
                            if oc.id_orden_compra not in fallback_oc_ids:
                                fallback_oc_ids.append(oc.id_orden_compra)
                    if not fallback_oc_ids and g.oc_compra_ref:
                        for n in re.findall(r"\d+", str(g.oc_compra_ref)):
                            num = int(n)
                            if num not in fallback_oc_ids:
                                fallback_oc_ids.append(num)

                    target_ocs = primary_oc_ids if primary_oc_ids else fallback_oc_ids

                    entrances.append({
                        "id_guia_servicio": g.id_guia_costo_servicio,
                        "id_orden_servicio": None,
                        "numero_guia_servicio": g.numero_guia,
                        "fecha": g.fecha_despacho or g.fecha_registro,
                        "tipo": "GUIA_COSTO_SERVICIO",
                        "proceso": dp.proceso or "Entrada a cepillado / proceso",
                        "origen": dp.origen_entrada or g.origen,
                        "destino": g.destino,
                        "target_oc_ids": target_ocs,
                        "raw_oc": dp.oc_compra_entrada or g.oc_compra_ref,
                        "espesor": float(dp.espesor_entrada) if dp.espesor_entrada is not None else None,
                        "ancho": float(dp.ancho_entrada) if dp.ancho_entrada is not None else None,
                        "largo": float(dp.largo_entrada) if dp.largo_entrada is not None else None,
                        "piezas": pzs_in,
                        "volumen": vol_in,
                    })

        # Si no había detalles_proceso pero hay resumen_general con 'Entrada'
        if not has_dp and g.resumen_general:
            for rg in g.resumen_general:
                mov = (rg.movimiento or "").upper()
                if "ENTRADA" in mov:
                    vol_in = float(rg.volumen_m3 or 0)
                    if vol_in > 0:
                        primary_oc_ids = []
                        if rg.oc_tabla:
                            primary_oc_ids.extend([int(n) for n in re.findall(r"\d+", str(rg.oc_tabla))])

                        fallback_oc_ids = list(primary_oc_ids)
                        if g.ordenes_compra:
                            for oc in g.ordenes_compra:
                                if oc.id_orden_compra not in fallback_oc_ids:
                                    fallback_oc_ids.append(oc.id_orden_compra)
                        if not fallback_oc_ids and g.oc_compra_ref:
                            for n in re.findall(r"\d+", str(g.oc_compra_ref)):
                                num = int(n)
                                if num not in fallback_oc_ids:
                                    fallback_oc_ids.append(num)

                        target_ocs = primary_oc_ids if primary_oc_ids else fallback_oc_ids

                        entrances.append({
                            "id_guia_servicio": g.id_guia_costo_servicio,
                            "id_orden_servicio": None,
                            "numero_guia_servicio": g.numero_guia,
                            "fecha": g.fecha_despacho or g.fecha_registro,
                            "tipo": "GUIA_COSTO_SERVICIO",
                            "proceso": rg.movimiento or "Entrada a servicio",
                            "origen": g.origen,
                            "destino": g.destino,
                            "target_oc_ids": target_ocs,
                            "raw_oc": rg.oc_tabla or g.oc_compra_ref,
                            "espesor": None,
                            "ancho": None,
                            "largo": None,
                            "piezas": 0.0,
                            "volumen": vol_in,
                        })

    # 2. Órdenes de Servicio
    ordenes_servicio = db.query(OrdenServicio).all()
    for os_obj in ordenes_servicio:
        if os_obj.id_orden_compra and os_obj.DetalleOrdenServicio:
            for dos in os_obj.DetalleOrdenServicio:
                vol_dos = float(dos.volumen_eq or dos.volumen or dos.cantidad or 0)
                pzs_dos = float(dos.piezas or 0)
                if vol_dos > 0 or pzs_dos > 0:
                    entrances.append({
                        "id_guia_servicio": None,
                        "id_orden_servicio": os_obj.id_orden_servicio,
                        "numero_guia_servicio": f"OS-{os_obj.id_orden_servicio}",
                        "fecha": os_obj.fecha_emision,
                        "tipo": "ORDEN_SERVICIO",
                        "proceso": os_obj.servicio or "Orden de Servicio",
                        "origen": None,
                        "destino": os_obj.destino,
                        "target_oc_ids": [os_obj.id_orden_compra],
                        "raw_oc": f"OC-{os_obj.id_orden_compra}",
                        "espesor": float(dos.espesor) if dos.espesor else None,
                        "ancho": float(dos.ancho) if dos.ancho else None,
                        "largo": float(dos.largo) if dos.largo else None,
                        "piezas": pzs_dos,
                        "volumen": vol_dos,
                    })

    return entrances


def calculate_transitorio_consumo_map(db: Session) -> Dict[int, Dict[str, Any]]:
    """
    Calcula el volumen y piezas utilizados en servicio para cada ítem de InventarioTransitorio.
    Retorna un diccionario: id_inventario_transitorio -> datos de consumo.
    """
    # 1. Obtener todos los ítems de InventarioTransitorio ordenados cronológicamente (FIFO)
    items = (
        db.query(InventarioTransitorio)
        .order_by(
            InventarioTransitorio.fecha_recepcion.asc(),
            InventarioTransitorio.id_inventario_transitorio.asc(),
        )
        .all()
    )

    consumo_map: Dict[int, Dict[str, Any]] = {}
    items_by_oc: Dict[int, List[Dict[str, Any]]] = {}

    for it in items:
        vol_rec = float(it.volumen_eq or it.volumen or it.cantidad or 0)
        pzs_rec = float(it.piezas or 0)
        entry = {
            "id_inventario_transitorio": it.id_inventario_transitorio,
            "id_orden_compra": it.id_orden_compra,
            "espesor": it.espesor,
            "ancho": it.ancho,
            "largo": it.largo,
            "recibido_volumen": round(vol_rec, 3),
            "recibido_piezas": round(pzs_rec, 2),
            "volumen_utilizado": 0.0,
            "piezas_utilizadas": 0.0,
            "saldo_volumen": round(vol_rec, 3),
            "saldo_piezas": round(pzs_rec, 2),
            "porcentaje_utilizado": 0.0,
            "estado_consumo": "DISPONIBLE",
            "entradas_servicio": [],
        }
        consumo_map[it.id_inventario_transitorio] = entry

        oc_id = it.id_orden_compra
        if oc_id:
            if oc_id not in items_by_oc:
                items_by_oc[oc_id] = []
            items_by_oc[oc_id].append(entry)

    # 2. Obtener todas las entradas de servicio registradas
    service_entrances = get_all_service_entrances(db)

    # 3. Aplicar descuento FIFO por OC y Escuadría
    for se in service_entrances:
        target_ocs = se.get("target_oc_ids") or []
        vol_to_deduct = float(se.get("volumen") or 0)
        pzs_to_deduct = float(se.get("piezas") or 0)

        if vol_to_deduct <= 0 and pzs_to_deduct <= 0:
            continue

        for oc_id in target_ocs:
            if oc_id not in items_by_oc:
                continue

            candidate_items = items_by_oc[oc_id]

            # Prioridad 1: Coincidencia de dimensiones (espesor y ancho)
            matched_by_dim = []
            if se.get("espesor") is not None and se.get("ancho") is not None:
                for c in candidate_items:
                    if _dim_eq(c.get("espesor"), se.get("espesor")) and _dim_eq(c.get("ancho"), se.get("ancho")):
                        if se.get("largo") is not None:
                            if _dim_eq(c.get("largo"), se.get("largo")):
                                matched_by_dim.append(c)
                        else:
                            matched_by_dim.append(c)

                # Si no hubo coincidencia completa con largo, usar solo espesor y ancho
                if not matched_by_dim and se.get("espesor") is not None and se.get("ancho") is not None:
                    matched_by_dim = [
                        c for c in candidate_items
                        if _dim_eq(c.get("espesor"), se.get("espesor")) and _dim_eq(c.get("ancho"), se.get("ancho"))
                    ]

            pool = matched_by_dim if matched_by_dim else candidate_items

            for c in pool:
                if vol_to_deduct <= 0.0001 and pzs_to_deduct <= 0.0001:
                    break

                avail_vol = max(0.0, c["recibido_volumen"] - c["volumen_utilizado"])
                avail_pzs = max(0.0, c["recibido_piezas"] - c["piezas_utilizadas"])

                if avail_vol <= 0.0001 and avail_pzs <= 0.0001:
                    continue

                take_vol = min(vol_to_deduct, avail_vol) if vol_to_deduct > 0 else 0.0
                take_pzs = min(pzs_to_deduct, avail_pzs) if pzs_to_deduct > 0 else 0.0

                c["volumen_utilizado"] = round(c["volumen_utilizado"] + take_vol, 3)
                c["piezas_utilizadas"] = round(c["piezas_utilizadas"] + take_pzs, 2)
                c["saldo_volumen"] = round(max(0.0, c["recibido_volumen"] - c["volumen_utilizado"]), 3)
                c["saldo_piezas"] = round(max(0.0, c["recibido_piezas"] - c["piezas_utilizadas"]), 2)

                vol_to_deduct = max(0.0, vol_to_deduct - take_vol)
                pzs_to_deduct = max(0.0, pzs_to_deduct - take_pzs)

                # Registrar detalle de entrada en el ítem solo si se consumió volumen o piezas
                if take_vol > 0 or take_pzs > 0:
                    c["entradas_servicio"].append({
                        "id_guia_servicio": se.get("id_guia_servicio"),
                        "id_orden_servicio": se.get("id_orden_servicio"),
                        "numero_guia_servicio": se.get("numero_guia_servicio"),
                        "fecha": se.get("fecha").isoformat() if hasattr(se.get("fecha"), "isoformat") else se.get("fecha"),
                        "tipo": se.get("tipo"),
                        "proceso": se.get("proceso"),
                        "origen": se.get("origen"),
                        "destino": se.get("destino"),
                        "volumen_utilizado": round(take_vol, 3),
                        "piezas_utilizadas": round(take_pzs, 2),
                        "raw_oc": se.get("raw_oc"),
                    })

            if vol_to_deduct <= 0.0001 and pzs_to_deduct <= 0.0001:
                break

    # 4. Calcular porcentaje y estado final de cada ítem
    for it_id, c in consumo_map.items():
        rec_vol = c["recibido_volumen"]
        ut_vol = c["volumen_utilizado"]
        pct = (ut_vol / rec_vol * 100.0) if rec_vol > 0 else 0.0
        c["porcentaje_utilizado"] = round(min(100.0, pct), 1)

        if ut_vol <= 0.0001:
            c["estado_consumo"] = "DISPONIBLE"
        elif c["saldo_volumen"] <= 0.001:
            c["estado_consumo"] = "CONSUMIDO"
        else:
            c["estado_consumo"] = "PARCIAL"

    return consumo_map


def enrich_item_dict(item_dict: Dict[str, Any], consumo_map: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Enriquece el diccionario de un ítem con sus métricas de consumo y descuento.
    """
    it_id = item_dict.get("id_inventario_transitorio")
    consumo = consumo_map.get(it_id) if it_id else None

    if consumo:
        item_dict["volumen_utilizado"] = consumo["volumen_utilizado"]
        item_dict["piezas_utilizadas"] = consumo["piezas_utilizadas"]
        item_dict["saldo_volumen"] = consumo["saldo_volumen"]
        item_dict["saldo_piezas"] = consumo["saldo_piezas"]
        item_dict["porcentaje_utilizado"] = consumo["porcentaje_utilizado"]
        item_dict["estado_consumo"] = consumo["estado_consumo"]
        item_dict["entradas_servicio"] = consumo["entradas_servicio"]
    else:
        vol = float(item_dict.get("volumen_eq") or item_dict.get("volumen") or item_dict.get("cantidad") or 0)
        pzs = float(item_dict.get("piezas") or 0)
        item_dict["volumen_utilizado"] = 0.0
        item_dict["piezas_utilizadas"] = 0.0
        item_dict["saldo_volumen"] = round(vol, 3)
        item_dict["saldo_piezas"] = round(pzs, 2)
        item_dict["porcentaje_utilizado"] = 0.0
        item_dict["estado_consumo"] = "DISPONIBLE"
        item_dict["entradas_servicio"] = []

    return item_dict


def enrich_guia_dict(guia_dict: Dict[str, Any], consumo_map: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Enriquece el diccionario de una guía y sus detalles con las métricas de consumo y descuento.
    """
    detalles = guia_dict.get("detalles") or []
    enriched_detalles = [enrich_item_dict(d, consumo_map) for d in detalles]
    guia_dict["detalles"] = enriched_detalles

    tot_vol = float(guia_dict.get("total_volumen") or sum(d.get("volumen_eq") or d.get("volumen") or 0 for d in enriched_detalles))
    tot_pzs = float(guia_dict.get("total_piezas") or sum(d.get("piezas") or 0 for d in enriched_detalles))

    tot_ut_vol = sum(d.get("volumen_utilizado", 0.0) for d in enriched_detalles)
    tot_ut_pzs = sum(d.get("piezas_utilizadas", 0.0) for d in enriched_detalles)

    saldo_vol = max(0.0, tot_vol - tot_ut_vol)
    saldo_pzs = max(0.0, tot_pzs - tot_ut_pzs)

    pct_guia = (tot_ut_vol / tot_vol * 100.0) if tot_vol > 0 else 0.0

    if tot_ut_vol <= 0.0001:
        est_guia = "DISPONIBLE"
    elif saldo_vol <= 0.001:
        est_guia = "CONSUMIDO"
    else:
        est_guia = "PARCIAL"

    # Consolidar entradas de servicio de todos los items sin duplicados exactos
    seen_servicios = set()
    guia_entradas = []
    for d in enriched_detalles:
        for ent in d.get("entradas_servicio", []):
            key = (ent.get("numero_guia_servicio"), ent.get("proceso"), ent.get("fecha"))
            if key not in seen_servicios:
                seen_servicios.add(key)
                guia_entradas.append(ent)

    guia_dict["total_volumen_utilizado"] = round(tot_ut_vol, 3)
    guia_dict["total_piezas_utilizadas"] = round(tot_ut_pzs, 2)
    guia_dict["total_saldo_volumen"] = round(saldo_vol, 3)
    guia_dict["total_saldo_piezas"] = round(saldo_pzs, 2)
    guia_dict["porcentaje_utilizado"] = round(min(100.0, pct_guia), 1)
    guia_dict["estado_consumo"] = est_guia
    guia_dict["entradas_servicio"] = guia_entradas

    return guia_dict


def get_transitorio_consumo_resumen(db: Session, id_bodega: Optional[int] = None) -> Dict[str, Any]:
    """
    Calcula el resumen general de inventario transitorio incluyendo:
    - Madera recibida (volumen, piezas, paquetes)
    - Madera utilizada en servicio (volumen, piezas, porcentaje)
    - Saldo disponible en inventario transitorio (volumen, piezas)
    - Costos (total, utilizado, saldo)
    - Desglose detallado por Orden de Compra (OC)
    - Desglose por Bodega y por Producto
    """
    consumo_map = calculate_transitorio_consumo_map(db)

    q = db.query(InventarioTransitorio)
    if id_bodega:
        q = q.filter(InventarioTransitorio.id_bodega == id_bodega)
    items = q.all()

    item_dicts = [enrich_item_dict(it.to_dict(), consumo_map) for it in items]

    total_volumen = round(sum(d.get("volumen") or d.get("volumen_eq") or 0 for d in item_dicts), 3)
    total_volumen_eq = round(sum(d.get("volumen_eq") or d.get("volumen") or 0 for d in item_dicts), 3)
    total_piezas = round(sum(d.get("piezas") or 0 for d in item_dicts), 2)
    total_paquetes = sum(d.get("numero_paquetes") or 1 for d in item_dicts)
    total_items = len(item_dicts)

    total_volumen_utilizado = round(sum(d.get("volumen_utilizado") or 0 for d in item_dicts), 3)
    total_piezas_utilizadas = round(sum(d.get("piezas_utilizadas") or 0 for d in item_dicts), 2)

    total_saldo_volumen = round(max(0.0, total_volumen_eq - total_volumen_utilizado), 3)
    total_saldo_piezas = round(max(0.0, total_piezas - total_piezas_utilizadas), 2)

    pct_utilizado = round((total_volumen_utilizado / total_volumen_eq * 100.0), 1) if total_volumen_eq > 0 else 0.0

    total_costo_producto = round(sum(d.get("subtotal") or 0 for d in item_dicts), 2)

    # Costo utilizado proporcional
    ratio_utilizado = (total_volumen_utilizado / total_volumen_eq) if total_volumen_eq > 0 else 0.0
    total_costo_utilizado = round(total_costo_producto * ratio_utilizado, 2)
    total_costo_saldo = round(max(0.0, total_costo_producto - total_costo_utilizado), 2)

    # Fletes
    from app.models.guia_costo_servicio import GuiaCostoServicio
    os_ids = set()
    for t in items:
        if t.id_orden_compra:
            linked_os = db.query(OrdenServicio).filter(OrdenServicio.id_orden_compra == t.id_orden_compra).all()
            for los in linked_os:
                os_ids.add(los.id_orden_servicio)

    guias_numeros = {t.numero_guia for t in items if t.numero_guia}
    for gnum in guias_numeros:
        gcs = db.query(GuiaCostoServicio).filter(GuiaCostoServicio.numero_guia == gnum).first()
        if gcs:
            for los in gcs.ordenes_servicio:
                os_ids.add(los.id_orden_servicio)

    total_flete = 0.0
    for os_id in os_ids:
        os_rec = db.query(OrdenServicio).filter(OrdenServicio.id_orden_servicio == os_id).first()
        if os_rec and os_rec.flete:
            total_flete += float(os_rec.flete)
    total_flete = round(total_flete, 2)
    total_costo = round(total_costo_producto + total_flete, 2)

    # Desglose por Orden de Compra (OC)
    oc_groups: Dict[int, Dict[str, Any]] = {}
    for d in item_dicts:
        oc_id = d.get("id_orden_compra") or 0
        prov = d.get("proveedor_nombre") or "Sin Proveedor"
        if oc_id not in oc_groups:
            oc_groups[oc_id] = {
                "id_orden_compra": oc_id,
                "proveedor_nombre": prov,
                "total_volumen": 0.0,
                "volumen_utilizado": 0.0,
                "saldo_volumen": 0.0,
                "total_piezas": 0.0,
                "piezas_utilizadas": 0.0,
                "saldo_piezas": 0.0,
                "items_count": 0,
                "costo_producto": 0.0,
                "guias_recepcion": set(),
                "guias_servicio": set(),
                "entradas_servicio": [],
            }

        g = oc_groups[oc_id]
        v_eq = d.get("volumen_eq") or d.get("volumen") or 0.0
        pzs = d.get("piezas") or 0.0
        v_ut = d.get("volumen_utilizado") or 0.0
        p_ut = d.get("piezas_utilizadas") or 0.0

        g["total_volumen"] += v_eq
        g["volumen_utilizado"] += v_ut
        g["total_piezas"] += pzs
        g["piezas_utilizadas"] += p_ut
        g["items_count"] += 1
        g["costo_producto"] += (d.get("subtotal") or 0.0)
        if d.get("numero_guia"):
            g["guias_recepcion"].add(d["numero_guia"])

        for ent in d.get("entradas_servicio", []):
            if ent.get("numero_guia_servicio"):
                g["guias_servicio"].add(ent["numero_guia_servicio"])
            g["entradas_servicio"].append(ent)

    desglose_por_oc = []
    for oc_id, g in oc_groups.items():
        g["total_volumen"] = round(g["total_volumen"], 3)
        g["volumen_utilizado"] = round(g["volumen_utilizado"], 3)
        g["saldo_volumen"] = round(max(0.0, g["total_volumen"] - g["volumen_utilizado"]), 3)
        g["total_piezas"] = round(g["total_piezas"], 2)
        g["piezas_utilizadas"] = round(g["piezas_utilizadas"], 2)
        g["saldo_piezas"] = round(max(0.0, g["total_piezas"] - g["piezas_utilizadas"]), 2)
        g["costo_producto"] = round(g["costo_producto"], 2)
        g["porcentaje_utilizado"] = round((g["volumen_utilizado"] / g["total_volumen"] * 100.0), 1) if g["total_volumen"] > 0 else 0.0

        if g["volumen_utilizado"] <= 0.0001:
            g["estado_consumo"] = "DISPONIBLE"
        elif g["saldo_volumen"] <= 0.001:
            g["estado_consumo"] = "CONSUMIDO"
        else:
            g["estado_consumo"] = "PARCIAL"

        g["guias_recepcion"] = sorted(list(g["guias_recepcion"]))
        g["guias_servicio"] = sorted(list(g["guias_servicio"]))

        # Unique service entrances
        seen_s = set()
        unique_entradas = []
        for e in g["entradas_servicio"]:
            k = (e.get("numero_guia_servicio"), e.get("proceso"), e.get("fecha"))
            if k not in seen_s:
                seen_s.add(k)
                unique_entradas.append(e)
        g["entradas_servicio"] = unique_entradas

        desglose_por_oc.append(g)

    desglose_por_oc.sort(key=lambda x: x["total_volumen"], reverse=True)

    # Breakdown by bodega
    bodega_groups: Dict[Any, Dict[str, Any]] = {}
    for d in item_dicts:
        bid = d.get("id_bodega")
        bname = d.get("bodega_nombre") or "Sin Bodega"
        if bid not in bodega_groups:
            bodega_groups[bid] = {
                "id_bodega": bid,
                "nombre": bname,
                "volumen": 0.0,
                "volumen_eq": 0.0,
                "volumen_utilizado": 0.0,
                "saldo_volumen": 0.0,
                "costo_producto": 0.0,
                "costo_flete": 0.0,
                "costo": 0.0,
                "items_count": 0,
                "paquetes_count": 0,
            }
        bg = bodega_groups[bid]
        bg["volumen"] += d.get("volumen") or 0.0
        bg["volumen_eq"] += d.get("volumen_eq") or 0.0
        bg["volumen_utilizado"] += d.get("volumen_utilizado") or 0.0
        bg["costo_producto"] += d.get("subtotal") or 0.0
        bg["items_count"] += 1
        bg["paquetes_count"] += d.get("numero_paquetes") or 1

    desglose_bodegas = []
    for bid, bg in bodega_groups.items():
        bg["volumen"] = round(bg["volumen"], 3)
        bg["volumen_eq"] = round(bg["volumen_eq"], 3)
        bg["volumen_utilizado"] = round(bg["volumen_utilizado"], 3)
        bg["saldo_volumen"] = round(max(0.0, bg["volumen_eq"] - bg["volumen_utilizado"]), 3)
        bg["costo_producto"] = round(bg["costo_producto"], 2)
        b_flete = round((bg["volumen"] / (total_volumen or 1)) * total_flete, 2) if total_volumen > 0 else 0.0
        bg["costo_flete"] = b_flete
        bg["costo"] = round(bg["costo_producto"] + b_flete, 2)
        desglose_bodegas.append(bg)

    desglose_bodegas.sort(key=lambda x: x["costo"], reverse=True)

    # Breakdown by producto
    prod_groups: Dict[Any, Dict[str, Any]] = {}
    for d in item_dicts:
        pid = d.get("id_producto")
        pname = d.get("producto_nombre") or d.get("texto_abierto") or "Sin Producto"
        if pid not in prod_groups:
            prod_groups[pid] = {
                "id_producto": pid,
                "nombre": pname,
                "volumen": 0.0,
                "volumen_eq": 0.0,
                "volumen_utilizado": 0.0,
                "saldo_volumen": 0.0,
                "costo_producto": 0.0,
                "costo_flete": 0.0,
                "costo": 0.0,
                "items_count": 0,
            }
        pg = prod_groups[pid]
        pg["volumen"] += d.get("volumen") or 0.0
        pg["volumen_eq"] += d.get("volumen_eq") or 0.0
        pg["volumen_utilizado"] += d.get("volumen_utilizado") or 0.0
        pg["costo_producto"] += d.get("subtotal") or 0.0
        pg["items_count"] += 1

    desglose_productos = []
    for pid, pg in prod_groups.items():
        pg["volumen"] = round(pg["volumen"], 3)
        pg["volumen_eq"] = round(pg["volumen_eq"], 3)
        pg["volumen_utilizado"] = round(pg["volumen_utilizado"], 3)
        pg["saldo_volumen"] = round(max(0.0, pg["volumen_eq"] - pg["volumen_utilizado"]), 3)
        pg["costo_producto"] = round(pg["costo_producto"], 2)
        p_flete = round((pg["volumen"] / (total_volumen or 1)) * total_flete, 2) if total_volumen > 0 else 0.0
        pg["costo_flete"] = p_flete
        pg["costo"] = round(pg["costo_producto"] + p_flete, 2)
        desglose_productos.append(pg)

    desglose_productos.sort(key=lambda x: x["costo"], reverse=True)

    return {
        "total_volumen": total_volumen,
        "total_volumen_eq": total_volumen_eq,
        "total_volumen_utilizado": total_volumen_utilizado,
        "total_saldo_volumen": total_saldo_volumen,
        "total_piezas": total_piezas,
        "total_piezas_utilizadas": total_piezas_utilizadas,
        "total_saldo_piezas": total_saldo_piezas,
        "porcentaje_utilizado": pct_utilizado,
        "total_costo_producto": total_costo_producto,
        "total_costo_utilizado": total_costo_utilizado,
        "total_costo_saldo": total_costo_saldo,
        "total_flete": total_flete,
        "total_costo": total_costo,
        "total_items": total_items,
        "total_paquetes": total_paquetes,
        "desglose_por_oc": desglose_por_oc,
        "desglose_bodegas": desglose_bodegas,
        "desglose_productos": desglose_productos,
    }
