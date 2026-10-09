from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Date
from sqlalchemy.orm import relationship, foreign
from app.db.base import Base
from datetime import date


class InventarioPuerto(Base):
    __tablename__ = "inventario_puerto"

    id_inventario_puerto = Column(Integer, primary_key=True, autoincrement=True)
    id_guia_inventario_puerto = Column(Integer, ForeignKey("guia_inventario_puerto.id_guia_inventario_puerto", ondelete="CASCADE"), nullable=True)

    id_orden_servicio = Column(Integer, ForeignKey("orden_servicio.id_orden_servicio"), nullable=True)
    id_detalle_os = Column(Integer, ForeignKey("detalle_orden_servicio.id_detalle_os"), nullable=True)
    id_orden_compra = Column(Integer, ForeignKey("orden_compra.id_orden_compra"), nullable=True)
    id_detalle_odc = Column(Integer, ForeignKey("detalle_orden_compra.id_detalle_odc"), nullable=True)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=True)
    id_bodega = Column(Integer, ForeignKey("bodega.id_bodega"), nullable=True)
    id_unidad_venta = Column(Integer, ForeignKey("unidad_venta.id_unidad_venta"), nullable=True)

    texto_abierto = Column(String(200), nullable=True)

    espesor = Column(String(20), nullable=True)
    id_unidad_medida_espesor = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"), nullable=True)

    ancho = Column(String(20), nullable=True)
    id_unidad_medida_ancho = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"), nullable=True)

    largo = Column(String(20), nullable=True)
    id_unidad_medida_largo = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"), nullable=True)

    cantidad = Column(Numeric(12, 3), nullable=True)
    precio_unitario = Column(Numeric(12, 3), nullable=True)
    subtotal = Column(Numeric(12, 3), nullable=True)

    volumen = Column(Numeric(12, 3), nullable=True)
    volumen_eq = Column(Numeric(12, 3), nullable=True)
    precio_eq = Column(Numeric(12, 3), nullable=True)
    piezas = Column(Numeric(12, 3), nullable=True)

    fecha_recepcion = Column(Date, default=date.today)
    numero_guia = Column(String(100), nullable=True)
    oc = Column(String(100), nullable=True)
    origen = Column(String(100), nullable=True)
    oc_compra = Column(String(100), nullable=True)
    etiqueta = Column(String(100), nullable=True)
    numero_paquetes = Column(Integer, nullable=True)
    url_documento = Column(String(500), nullable=True)
    observaciones = Column(String(500), nullable=True)
    estado = Column(String(50), default="RECIBIDO")

    # Relaciones
    guia = relationship(
        "GuiaInventarioPuerto",
        back_populates="detalles",
    )

    # Relaciones viewonly
    OrdenServicio = relationship(
        "OrdenServicio",
        primaryjoin="foreign(InventarioPuerto.id_orden_servicio)==OrdenServicio.id_orden_servicio",
        viewonly=True,
    )
    DetalleOrdenServicio = relationship(
        "DetalleOrdenServicio",
        primaryjoin="foreign(InventarioPuerto.id_detalle_os)==DetalleOrdenServicio.id_detalle_os",
        viewonly=True,
    )
    OrdenCompra = relationship(
        "OrdenCompra",
        primaryjoin="foreign(InventarioPuerto.id_orden_compra)==OrdenCompra.id_orden_compra",
        viewonly=True,
    )
    Producto = relationship(
        "Producto",
        primaryjoin="foreign(InventarioPuerto.id_producto)==Producto.id_producto",
        viewonly=True,
    )
    Bodega = relationship(
        "Bodega",
        primaryjoin="foreign(InventarioPuerto.id_bodega)==Bodega.id_bodega",
        viewonly=True,
    )
    UnidadVenta = relationship(
        "UnidadVenta",
        primaryjoin="foreign(InventarioPuerto.id_unidad_venta)==UnidadVenta.id_unidad_venta",
        viewonly=True,
    )

    def __repr__(self):
        return f"<InventarioPuerto {self.id_inventario_puerto}>"

    def to_dict(self):
        def _num(x):
            return float(x) if x is not None else None

        prod = self.Producto
        if not prod and self.id_producto:
            from sqlalchemy.orm import object_session
            sess = object_session(self)
            if sess:
                from app.models.producto import Producto
                prod = sess.get(Producto, self.id_producto)

        prod_nombre = None
        id_especie = None
        if prod:
            prod_nombre = getattr(prod, "nombre_producto_esp", None) or getattr(prod, "nombre", None) or getattr(prod, "nombre_producto_ing", None)
            id_especie = getattr(prod, "id_especie", None)

        uv = self.UnidadVenta
        if not uv and self.id_unidad_venta:
            from sqlalchemy.orm import object_session
            sess = object_session(self)
            if sess:
                from app.models.unidad_venta import UnidadVenta
                uv = sess.get(UnidadVenta, self.id_unidad_venta)

        uv_nombre = getattr(uv, "nombre", None) if uv else None

        bodega = self.Bodega
        if not bodega and self.id_bodega:
            from sqlalchemy.orm import object_session
            sess = object_session(self)
            if sess:
                from app.models.bodega import Bodega
                bodega = sess.get(Bodega, self.id_bodega)

        bodega_nombre = getattr(bodega, "nombre", None) if bodega else None

        proveedor_nombre = None
        os = self.OrdenServicio
        if not os and self.id_orden_servicio:
            from sqlalchemy.orm import object_session
            sess = object_session(self)
            if sess:
                from app.models.orden_servicio import OrdenServicio
                os = sess.get(OrdenServicio, self.id_orden_servicio)

        if os and getattr(os, "ClienteProveedor", None):
            proveedor_nombre = getattr(os.ClienteProveedor, "razon_social", None)
        else:
            odc = self.OrdenCompra
            if not odc and self.id_orden_compra:
                from sqlalchemy.orm import object_session
                sess = object_session(self)
                if sess:
                    from app.models.orden_compra import OrdenCompra
                    odc = sess.get(OrdenCompra, self.id_orden_compra)
            if odc and getattr(odc, "ClienteProveedor", None):
                proveedor_nombre = getattr(odc.ClienteProveedor, "razon_social", None)

        g = self.guia
        num_guia = self.numero_guia or (g.numero_guia if g else None)
        oc_val = self.oc or (g.oc if g else None)
        origen_val = self.origen or (g.origen if g else None)
        url_doc = self.url_documento or (g.url_documento if g else None)
        fecha_rec = self.fecha_recepcion or (g.fecha_recepcion if g else None)

        calc_pu = _num(self.precio_unitario)
        calc_peq = _num(self.precio_eq)
        calc_sub = _num(self.subtotal)

        from sqlalchemy.orm import object_session
        sess = object_session(self)

        def _dim_eq(v1, v2):
            if not v1 or not v2:
                return True
            try:
                return abs(float(str(v1).replace(",", ".")) - float(str(v2).replace(",", "."))) < 0.01
            except Exception:
                return str(v1).strip().lower() == str(v2).strip().lower()

        # 1. Costo Compra Base ($/m3) from origin OC (with SD/BS resolution and comision/flete addition)
        d_match = None
        if self.id_detalle_odc and sess:
            from app.models.detalle_orden_compra import DetalleOrdenCompra
            cand_det = sess.get(DetalleOrdenCompra, self.id_detalle_odc)
            if cand_det:
                if (self.espesor or self.ancho or self.largo) and not (_dim_eq(cand_det.espesor, self.espesor) and _dim_eq(cand_det.ancho, self.ancho) and _dim_eq(cand_det.largo, self.largo)):
                    d_match = None
                else:
                    d_match = cand_det

        candidate_oc_ids = []
        if self.id_orden_compra and self.id_orden_compra not in candidate_oc_ids:
            candidate_oc_ids.append(self.id_orden_compra)
        import re
        for raw_field in [self.oc_compra, self.oc, (self.guia.oc if self.guia else None)]:
            if raw_field:
                for num_str in re.findall(r"\d+", str(raw_field)):
                    num_int = int(num_str)
                    if num_int not in candidate_oc_ids:
                        candidate_oc_ids.append(num_int)

        if not d_match and candidate_oc_ids and sess:
            from app.models.detalle_orden_compra import DetalleOrdenCompra
            orig_dets = sess.query(DetalleOrdenCompra).filter(DetalleOrdenCompra.id_orden_compra.in_(candidate_oc_ids)).all()
            if orig_dets:
                # First try matching product and dimensions
                dim_matches = [d for d in orig_dets if _dim_eq(d.espesor, self.espesor) and _dim_eq(d.ancho, self.ancho) and _dim_eq(d.largo, self.largo)]
                
                raw_str = f"{self.oc_compra or ''} {self.oc or ''}".upper()
                is_sd = bool(re.search(r"\bSD\b", raw_str) or "SD" in raw_str)
                is_bs = bool(re.search(r"\bBS\b", raw_str) or "BS" in raw_str)

                pool = dim_matches if dim_matches else orig_dets
                if is_sd and pool:
                    d_match = max(pool, key=lambda d: float(d.precio_eq or d.precio_unitario or 0))
                elif is_bs and pool:
                    d_match = min(pool, key=lambda d: float(d.precio_eq or d.precio_unitario or 0))
                else:
                    prod_matches = [d for d in pool if self.id_producto and d.id_producto == self.id_producto]
                    d_match = prod_matches[0] if prod_matches else pool[0]

        comision_odc = 0.0
        flete_odc = 0.0
        if d_match:
            if d_match.precio_eq is not None and float(d_match.precio_eq) > 0:
                calc_peq = float(d_match.precio_eq)
            elif d_match.precio_unitario is not None and float(d_match.precio_unitario) > 0:
                calc_peq = float(d_match.precio_unitario)
            if d_match.precio_unitario is not None and float(d_match.precio_unitario) > 0:
                calc_pu = float(d_match.precio_unitario)
            comision_odc = round(float(getattr(d_match, "comision", 0) or 0.0), 2)
            flete_odc = round(float(getattr(d_match, "flete", 0) or 0.0), 2)

        precio_base_madera = round(float(calc_peq or calc_pu or 0.0), 2)
        costo_compra_m3 = round(precio_base_madera + comision_odc + flete_odc, 2)

        # 2. Guia Costo Servicio (volumen entrada / volumen salida y servicios)
        # volumen salida = guia costo servicio (flejes de 1 + flejes de 2)
        vol_in = 1.0
        vol_out = 1.0
        gcs = None
        servicios_m3 = 0.0
        total_vol_salida_gcs = 0.0

        if num_guia and sess:
            from app.models.guia_costo_servicio import GuiaCostoServicio
            gcs = sess.query(GuiaCostoServicio).filter(GuiaCostoServicio.numero_guia == str(num_guia).strip()).first()

        if gcs:
            # Calcular volumen total salida guia (flejes 1ra + flejes 2da)
            vol_1ra_tot = float(gcs.total_m3 or 0)
            vol_2da_tot = float(gcs.flejes_2da or 0)

            # Fallback a stock_planta si total_m3 o flejes_2da están vacíos
            if vol_1ra_tot <= 0 and gcs.stock_planta:
                vol_1ra_tot = sum(float(sp.volumen_m3 or 0) for sp in gcs.stock_planta if sp.tipo_stock and any(k in sp.tipo_stock.upper() for k in ["1RA", "1ERA", "1°", "1", "TERMINADO"]))
            if vol_2da_tot <= 0 and gcs.stock_planta:
                vol_2da_tot = sum(float(sp.volumen_m3 or 0) for sp in gcs.stock_planta if sp.tipo_stock and any(k in sp.tipo_stock.upper() for k in ["2DA", "2ERA", "2°", "2"]))

            # Fallback a resumen_general
            if vol_1ra_tot <= 0 and gcs.resumen_general:
                vol_1ra_tot = sum(
                    float(rg.volumen_m3 or 0)
                    for rg in gcs.resumen_general
                    if rg.movimiento and any(k in rg.movimiento.upper() for k in ["TERMINADO", "1RA", "1ERA", "1°", "FLEJES TERMINADO", "FLEJES 1RA", "FLEJES 1ERA"]) and "2DA" not in (rg.movimiento or "").upper()
                )
            if vol_2da_tot <= 0 and gcs.resumen_general:
                vol_2da_tot = sum(
                    float(rg.volumen_m3 or 0)
                    for rg in gcs.resumen_general
                    if rg.movimiento and any(k in rg.movimiento.upper() for k in ["2DA", "2ERA", "2°", "FLEJES 2DA", "FLEJES 2ERA"])
                )

            total_vol_salida_gcs = vol_1ra_tot + vol_2da_tot
            if total_vol_salida_gcs <= 0 and gcs.detalles_proceso:
                total_vol_salida_gcs = sum(float(dp.volumen_m3_salida or 0) for dp in gcs.detalles_proceso)
            if total_vol_salida_gcs <= 0 and g and g.detalles:
                total_vol_salida_gcs = sum(float(it.volumen_eq or it.volumen or 0) for it in g.detalles)

            total_servicios_usd = float(gcs.total_usd or 0)
            if not total_servicios_usd and gcs.detalles:
                total_servicios_usd = sum(float(d.total_usd or 0) for d in gcs.detalles)

            servicios_m3 = round(total_servicios_usd / total_vol_salida_gcs, 2) if total_vol_salida_gcs > 0 else 0.0

            # Construir bloques de resumen general por entrada/salida (Entrada rustico vs Flejes 1ra + Flejes 2da)
            rg_blocks = []
            curr_b = None
            if gcs.resumen_general:
                for rg in gcs.resumen_general:
                    mov = str(rg.movimiento or "").upper()
                    v = float(rg.volumen_m3 or 0)
                    if "ENTRADA" in mov or "RUSTICO" in mov or curr_b is None:
                        curr_b = {
                            "oc": str(rg.oc_tabla or ""),
                            "in": v if ("ENTRADA" in mov or "RUSTICO" in mov) else 0.0,
                            "1ra": 0.0,
                            "2da": 0.0,
                        }
                        rg_blocks.append(curr_b)
                    else:
                        if any(k in mov for k in ["2DA", "2ERA", "2°", "FLEJES 2DA", "FLEJES 2ERA"]):
                            curr_b["2da"] += v
                        elif any(k in mov for k in ["TERMINADO", "1RA", "1ERA", "1°", "FLEJES"]):
                            curr_b["1ra"] += v

            oc_raw = str(self.oc_compra or self.oc or "")
            matched_b = None
            if rg_blocks and candidate_oc_ids:
                is_sd = "SD" in oc_raw.upper()
                is_bs = "BS" in oc_raw.upper()
                for b in rg_blocks:
                    b_oc = b["oc"]
                    if any(str(cid) in b_oc for cid in candidate_oc_ids):
                        b_sd = "SD" in b_oc.upper()
                        b_bs = "BS" in b_oc.upper()
                        if (is_sd and b_sd) or (is_bs and b_bs) or (not is_sd and not is_bs and not b_sd and not b_bs) or (not b_sd and not b_bs):
                            matched_b = b
                            break

            if matched_b and (matched_b["1ra"] + matched_b["2da"]) > 0:
                vol_in = matched_b["in"] if matched_b["in"] > 0 else 1.0
                vol_out = matched_b["1ra"] + matched_b["2da"]
            else:
                # Match en detalles_proceso de GCS
                matched_dp = None
                if gcs.detalles_proceso:
                    for dp in gcs.detalles_proceso:
                        dp_oc = str(dp.oc_compra_entrada or "")
                        if any(str(cid) in dp_oc for cid in candidate_oc_ids):
                            is_sd = "SD" in oc_raw.upper()
                            is_bs = "BS" in oc_raw.upper()
                            dp_sd = "SD" in dp_oc.upper()
                            dp_bs = "BS" in dp_oc.upper()
                            if (is_sd and dp_sd) or (is_bs and dp_bs) or (not is_sd and not is_bs and not dp_sd and not dp_bs):
                                matched_dp = dp
                                break
                            elif not matched_dp:
                                matched_dp = dp
                    if not matched_dp and len(gcs.detalles_proceso) == 1:
                        matched_dp = gcs.detalles_proceso[0]

                if matched_dp and matched_dp.volumen_m3_entrada:
                    vol_in = float(matched_dp.volumen_m3_entrada)
                    if len(gcs.detalles_proceso) == 1 and total_vol_salida_gcs > 0:
                        vol_out = total_vol_salida_gcs
                    elif matched_dp.volumen_m3_salida:
                        dp_out_raw = float(matched_dp.volumen_m3_salida)
                        sum_dp_out = sum(float(dp.volumen_m3_salida or 0) for dp in gcs.detalles_proceso)
                        if sum_dp_out > 0 and total_vol_salida_gcs > 0:
                            vol_out = (dp_out_raw / sum_dp_out) * total_vol_salida_gcs
                        else:
                            vol_out = dp_out_raw
                elif total_vol_salida_gcs > 0:
                    vol_out = total_vol_salida_gcs

            # Safety fallback: si por alguna razón vol_out quedó en <= 0 o con un ratio irreal
            if (vol_out <= 0 or (vol_in / vol_out > 5.0)) and total_vol_salida_gcs > 0:
                vol_out = total_vol_salida_gcs

        # 3. Costo Madera Ajustado ($/m3): ((volumen entrada * costo compra) / volumen salida)
        costo_madera_m3 = round((vol_in * costo_compra_m3) / vol_out, 2) if (vol_out and vol_out > 0) else round(costo_compra_m3, 2)

        # 4. Orden de Servicio (Flete $/m3)
        # ya que puede o no tener orden de servicio
        os_obj = os
        if not os_obj and g and g.id_orden_servicio and sess:
            from app.models.orden_servicio import OrdenServicio
            os_obj = sess.get(OrdenServicio, g.id_orden_servicio)
        if not os_obj and gcs and gcs.ordenes_servicio:
            os_obj = gcs.ordenes_servicio[0]
        if not os_obj and self.id_orden_compra and sess:
            from app.models.orden_servicio import OrdenServicio
            os_obj = sess.query(OrdenServicio).filter(OrdenServicio.id_orden_compra == self.id_orden_compra).first()
        if not os_obj and g and g.id_orden_compra and sess:
            from app.models.orden_servicio import OrdenServicio
            os_obj = sess.query(OrdenServicio).filter(OrdenServicio.id_orden_compra == g.id_orden_compra).first()

        flete_m3 = 0.0
        tiene_os = False
        id_os_linked = self.id_orden_servicio
        if os_obj:
            tiene_os = True
            id_os_linked = os_obj.id_orden_servicio
            if os_obj.flete:
                flete_total = float(os_obj.flete)
                divisor_vol = total_vol_salida_gcs if total_vol_salida_gcs > 0 else (_num(self.volumen_eq) or _num(self.volumen) or 1.0)
                flete_m3 = round(flete_total / divisor_vol, 2)

        # 5. Costo Final (Unitario y Totales)
        # Formula: ((cantidad volumen entrada x costo compra) / volumen salida) + servicios + flete
        costo_final_unitario = round(costo_madera_m3 + servicios_m3 + flete_m3, 2)
        vol_item = _num(self.volumen_eq) or _num(self.volumen) or _num(self.cantidad) or 0.0
        costo_final_total = round(vol_item * costo_final_unitario, 2)
        costo_madera_total = round(vol_item * costo_madera_m3, 2)
        costo_servicios_total = round(vol_item * servicios_m3, 2)
        costo_flete_total = round(vol_item * flete_m3, 2)
        calc_sub = costo_madera_total

        return {
            "id_inventario_puerto": self.id_inventario_puerto,
            "id_guia_inventario_puerto": self.id_guia_inventario_puerto,
            "id_orden_servicio": id_os_linked,
            "id_detalle_os": self.id_detalle_os,
            "id_orden_compra": self.id_orden_compra,
            "id_detalle_odc": self.id_detalle_odc,
            "id_producto": self.id_producto,
            "id_especie": id_especie,
            "producto_nombre": prod_nombre,
            "id_bodega": self.id_bodega,
            "bodega_nombre": bodega_nombre,
            "proveedor_nombre": proveedor_nombre,
            "texto_abierto": self.texto_abierto,
            "id_unidad_venta": self.id_unidad_venta,
            "unidad_venta_nombre": uv_nombre,
            "cantidad": _num(self.cantidad),
            "espesor": self.espesor,
            "id_unidad_medida_espesor": self.id_unidad_medida_espesor,
            "ancho": self.ancho,
            "id_unidad_medida_ancho": self.id_unidad_medida_ancho,
            "largo": self.largo,
            "id_unidad_medida_largo": self.id_unidad_medida_largo,
            "precio_unitario": calc_pu,
            "subtotal": calc_sub,
            "volumen": _num(self.volumen),
            "volumen_eq": _num(self.volumen_eq),
            "precio_eq": calc_peq,
            "piezas": _num(self.piezas),
            "fecha_recepcion": fecha_rec.isoformat() if hasattr(fecha_rec, "isoformat") else fecha_rec,
            "numero_guia": num_guia,
            "oc": oc_val,
            "origen": origen_val,
            "oc_compra": self.oc_compra,
            "etiqueta": self.etiqueta,
            "numero_paquetes": self.numero_paquetes,
            "url_documento": url_doc,
            "observaciones": self.observaciones,
            "estado": self.estado,
            "costo_compra_m3": round(costo_compra_m3, 2),
            "precio_base_madera": round(precio_base_madera, 2),
            "comision_odc": round(comision_odc, 2),
            "flete_odc": round(flete_odc, 2),
            "volumen_entrada_proceso": round(vol_in, 4) if vol_in != 1.0 else None,
            "volumen_salida_proceso": round(vol_out, 4) if vol_out != 1.0 else None,
            "costo_madera_m3": costo_madera_m3,
            "servicios_m3": servicios_m3,
            "flete_m3": flete_m3,
            "costo_final_unitario": costo_final_unitario,
            "costo_final_total": costo_final_total,
            "costo_madera_total": costo_madera_total,
            "costo_servicios_total": costo_servicios_total,
            "costo_flete_total": costo_flete_total,
            "tiene_orden_servicio": tiene_os,
        }
