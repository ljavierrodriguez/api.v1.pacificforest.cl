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

    espesor_entrada = Column(String(20), nullable=True)
    ancho_entrada = Column(String(20), nullable=True)
    largo_entrada = Column(String(20), nullable=True)
    piezas_entrada = Column(Numeric(12, 3), nullable=True)
    volumen_entrada = Column(Numeric(12, 3), nullable=True)

    espesor_real = Column(String(20), nullable=True)
    ancho_real = Column(String(20), nullable=True)
    largo_real = Column(String(20), nullable=True)
    piezas_real = Column(Numeric(12, 3), nullable=True)
    volumen_real = Column(Numeric(12, 3), nullable=True)

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

        from sqlalchemy.orm import object_session, selectinload
        sess = object_session(self)

        prod = self.__dict__.get("Producto")
        if not prod and self.id_producto:
            if sess:
                from app.models.producto import Producto
                prod = sess.get(Producto, self.id_producto)
            else:
                prod = self.Producto

        prod_nombre = None
        id_especie = None
        if prod:
            prod_nombre = getattr(prod, "nombre_producto_esp", None) or getattr(prod, "nombre", None) or getattr(prod, "nombre_producto_ing", None)
            id_especie = getattr(prod, "id_especie", None)

        uv = self.__dict__.get("UnidadVenta")
        if not uv and self.id_unidad_venta:
            if sess:
                from app.models.unidad_venta import UnidadVenta
                uv = sess.get(UnidadVenta, self.id_unidad_venta)
            else:
                uv = self.UnidadVenta

        uv_nombre = getattr(uv, "nombre", None) if uv else None

        bodega = self.__dict__.get("Bodega")
        if not bodega and self.id_bodega:
            if sess:
                from app.models.bodega import Bodega
                bodega = sess.get(Bodega, self.id_bodega)
            else:
                bodega = self.Bodega

        bodega_nombre = getattr(bodega, "nombre", None) if bodega else None

        proveedor_nombre = None
        os = self.__dict__.get("OrdenServicio")
        if not os and self.id_orden_servicio:
            if sess:
                from app.models.orden_servicio import OrdenServicio
                os = sess.get(OrdenServicio, self.id_orden_servicio)
            else:
                os = self.OrdenServicio

        if os and getattr(os, "id_cliente_proveedor", None) and sess:
            from app.models.cliente_proveedor import ClienteProveedor
            cp = sess.get(ClienteProveedor, os.id_cliente_proveedor)
            if cp:
                proveedor_nombre = getattr(cp, "razon_social", None)
        elif os and getattr(os, "ClienteProveedor", None):
            proveedor_nombre = getattr(os.ClienteProveedor, "razon_social", None)
        else:
            odc = self.__dict__.get("OrdenCompra")
            if not odc and self.id_orden_compra:
                if sess:
                    from app.models.orden_compra import OrdenCompra
                    odc = sess.get(OrdenCompra, self.id_orden_compra)
                else:
                    odc = self.OrdenCompra
            if odc and getattr(odc, "id_cliente_proveedor", None) and sess:
                from app.models.cliente_proveedor import ClienteProveedor
                cp = sess.get(ClienteProveedor, odc.id_cliente_proveedor)
                if cp:
                    proveedor_nombre = getattr(cp, "razon_social", None)
            elif odc and getattr(odc, "ClienteProveedor", None):
                proveedor_nombre = getattr(odc.ClienteProveedor, "razon_social", None)

        g = self.__dict__.get("guia")
        if not g and self.id_guia_inventario_puerto and sess:
            from app.models.guia_inventario_puerto import GuiaInventarioPuerto
            g = sess.get(GuiaInventarioPuerto, self.id_guia_inventario_puerto)
        elif not g:
            g = self.guia
        num_guia = self.numero_guia or (g.numero_guia if g else None)
        oc_val = self.oc or (g.oc if g else None)
        origen_val = self.origen or (g.origen if g else None)
        url_doc = self.url_documento or (g.url_documento if g else None)
        fecha_rec = self.fecha_recepcion or (g.fecha_recepcion if g else None)

        calc_pu = _num(self.precio_unitario)
        calc_peq = _num(self.precio_eq)
        calc_sub = _num(self.subtotal)

        esp_entrada = self.espesor_entrada if self.espesor_entrada is not None else self.espesor
        anc_entrada = self.ancho_entrada if self.ancho_entrada is not None else self.ancho
        lar_entrada = self.largo_entrada if self.largo_entrada is not None else self.largo
        pzs_entrada = _num(self.piezas_entrada) if self.piezas_entrada is not None else _num(self.piezas)
        vol_entrada = _num(self.volumen_entrada) if self.volumen_entrada is not None else (_num(self.volumen) or _num(self.volumen_eq))

        esp_real = self.espesor_real if self.espesor_real is not None else self.espesor
        anc_real = self.ancho_real if self.ancho_real is not None else self.ancho
        lar_real = self.largo_real if self.largo_real is not None else self.largo
        pzs_real = _num(self.piezas_real) if self.piezas_real is not None else _num(self.piezas)
        vol_real = _num(self.volumen_real) if self.volumen_real is not None else (_num(self.volumen_eq) or _num(self.volumen) or _num(self.cantidad) or 0.0)

        def _parse_dim(v):
            if v is None:
                return None
            s = str(v).strip().lower()
            if not s:
                return None
            import re
            m = re.match(r"^(\d+),(\d{3})$", s)
            if m:
                s = m.group(1) + m.group(2)
            try:
                return float(s.replace(",", "."))
            except Exception:
                return s

        def _dim_eq(v1, v2):
            if not v1 or not v2:
                return True
            p1 = _parse_dim(v1)
            p2 = _parse_dim(v2)
            if isinstance(p1, float) and isinstance(p2, float):
                return abs(p1 - p2) < 0.01
            return str(p1).strip().lower() == str(p2).strip().lower()

        # 1. Costo Compra Base ($/m3) from origin OC (with SD/BS resolution and comision/flete addition)
        import re
        candidate_oc_ids = []
        # Prioridad 1: OC de compra de origen del lote/paquete (oc_compra)
        if self.oc_compra:
            for num_str in re.findall(r"\d+", str(self.oc_compra)):
                num_int = int(num_str)
                if num_int not in candidate_oc_ids:
                    candidate_oc_ids.append(num_int)

        # Prioridad 2: Si no hubo oc_compra, recurrir a id_orden_compra, oc o guia.oc
        if not candidate_oc_ids:
            if self.id_orden_compra and self.id_orden_compra not in candidate_oc_ids:
                candidate_oc_ids.append(self.id_orden_compra)
            for raw_field in [self.oc, (self.guia.oc if self.guia else None)]:
                if raw_field:
                    for num_str in re.findall(r"\d+", str(raw_field)):
                        num_int = int(num_str)
                        if num_int not in candidate_oc_ids:
                            candidate_oc_ids.append(num_int)

        orig_dets = []
        if candidate_oc_ids and sess:
            from app.models.detalle_orden_compra import DetalleOrdenCompra
            odc_dets_cache = sess.info.setdefault("_odc_dets_cache", {})
            missing_cids = [cid for cid in candidate_oc_ids if cid not in odc_dets_cache]
            if missing_cids:
                fetched_dets = sess.query(DetalleOrdenCompra).filter(DetalleOrdenCompra.id_orden_compra.in_(missing_cids)).all()
                for cid in missing_cids:
                    odc_dets_cache[cid] = []
                for fd in fetched_dets:
                    odc_dets_cache.setdefault(fd.id_orden_compra, []).append(fd)
            for cid in candidate_oc_ids:
                orig_dets.extend(odc_dets_cache.get(cid, []))

        d_match = None
        if self.id_detalle_odc and sess:
            from app.models.detalle_orden_compra import DetalleOrdenCompra
            cand_det = next((d for d in orig_dets if d.id_detalle_odc == self.id_detalle_odc), None)
            if not cand_det:
                det_id_cache = sess.info.setdefault("_det_odc_by_id", {})
                if self.id_detalle_odc not in det_id_cache:
                    det_id_cache[self.id_detalle_odc] = sess.get(DetalleOrdenCompra, self.id_detalle_odc)
                cand_det = det_id_cache[self.id_detalle_odc]
            if cand_det:
                # Verificar que el detalle pertenezca a la OC origen correcta si existe candidate_oc_ids
                if candidate_oc_ids and cand_det.id_orden_compra not in candidate_oc_ids:
                    d_match = None
                elif (esp_entrada or anc_entrada or lar_entrada) and not (
                    (_dim_eq(cand_det.espesor, esp_entrada) and _dim_eq(cand_det.ancho, anc_entrada) and _dim_eq(cand_det.largo, lar_entrada))
                    or (_dim_eq(cand_det.espesor, esp_real) and _dim_eq(cand_det.ancho, anc_real) and _dim_eq(cand_det.largo, lar_real))
                ):
                    d_match = None
                else:
                    d_match = cand_det

        if not d_match and orig_dets:
                # First try matching product and dimensions (prioritizing escuadría entrada, then escuadría real)
                dim_matches = [
                    d for d in orig_dets
                    if _dim_eq(d.espesor, esp_entrada) and _dim_eq(d.ancho, anc_entrada) and _dim_eq(d.largo, lar_entrada)
                ]
                if not dim_matches:
                    dim_matches = [
                        d for d in orig_dets
                        if _dim_eq(d.espesor, esp_real) and _dim_eq(d.ancho, anc_real) and _dim_eq(d.largo, lar_real)
                    ]
                
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
        vol_out_1ra = 0.0
        vol_out_2da = 0.0
        gcs = None
        servicios_m3 = 0.0
        total_vol_salida_gcs = 0.0
        vol_1ra_tot = 0.0
        vol_2da_tot = 0.0

        if num_guia and sess:
            from app.models.guia_costo_servicio import GuiaCostoServicio
            gcs_key = str(num_guia).strip()
            gcs_cache = sess.info.setdefault("_gcs_cache", {})
            if gcs_key not in gcs_cache:
                gcs_cache[gcs_key] = (
                    sess.query(GuiaCostoServicio)
                    .options(
                        selectinload(GuiaCostoServicio.stock_planta),
                        selectinload(GuiaCostoServicio.resumen_general),
                        selectinload(GuiaCostoServicio.detalles),
                        selectinload(GuiaCostoServicio.detalles_proceso),
                        selectinload(GuiaCostoServicio.ordenes_servicio),
                    )
                    .filter(GuiaCostoServicio.numero_guia == gcs_key)
                    .first()
                )
            gcs = gcs_cache[gcs_key]

        if gcs:
            # Calcular volumen total salida guia (flejes 1ra + flejes 2da)
            # Para 2da: Consolidar total desde stock_planta o la suma de resumen_general si existen
            sum_sp_2da = sum(float(sp.volumen_m3 or 0) for sp in gcs.stock_planta if sp.tipo_stock and any(k in sp.tipo_stock.upper() for k in ["2DA", "2ERA", "2°", "2"])) if gcs.stock_planta else 0.0
            sum_rg_2da = sum(
                float(rg.volumen_m3 or 0)
                for rg in gcs.resumen_general
                if rg.movimiento and any(k in rg.movimiento.upper() for k in ["2DA", "2ERA", "2°", "FLEJES 2DA", "FLEJES 2ERA"])
            ) if gcs.resumen_general else 0.0

            # En el nuevo formato Excel el cuadro único de Stock Planta corresponde a 2da
            sp_all_is_2da = False
            if sum_sp_2da <= 0 and gcs.stock_planta:
                sum_sp_all = sum(float(sp.volumen_m3 or 0) for sp in gcs.stock_planta)
                f2da_hdr = float(gcs.flejes_2da or 0)
                t_m3_hdr = float(gcs.total_m3 or 0)
                if (f2da_hdr > 0 and abs(sum_sp_all - f2da_hdr) < 0.5) or (sum_rg_2da > 0 and abs(sum_sp_all - sum_rg_2da) < 0.5) or (t_m3_hdr > 0 and abs(sum_sp_all - t_m3_hdr) > 0.5):
                    sum_sp_2da = sum_sp_all
                    sp_all_is_2da = True

            if sum_sp_2da > 0:
                vol_2da_tot = sum_sp_2da
            elif sum_rg_2da > 0:
                vol_2da_tot = sum_rg_2da
            else:
                vol_2da_tot = float(gcs.flejes_2da or 0)

            # Para 1ra: total_m3 de cabecera o fallback a stock_planta / resumen_general
            vol_1ra_tot = float(gcs.total_m3 or 0)
            if vol_1ra_tot <= 0 and gcs.stock_planta and not sp_all_is_2da:
                vol_1ra_tot = sum(float(sp.volumen_m3 or 0) for sp in gcs.stock_planta if sp.tipo_stock and any(k in sp.tipo_stock.upper() for k in ["1RA", "1ERA", "1°", "1", "TERMINADO"]))
            if vol_1ra_tot <= 0 and gcs.resumen_general:
                vol_1ra_tot = sum(
                    float(rg.volumen_m3 or 0)
                    for rg in gcs.resumen_general
                    if rg.movimiento and any(k in rg.movimiento.upper() for k in ["TERMINADO", "1RA", "1ERA", "1°", "FLEJES TERMINADO", "FLEJES 1RA", "FLEJES 1ERA"]) and "2DA" not in (rg.movimiento or "").upper()
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

            # Si el último bloque del resumen general quedó con 2da=0 (por corte de fila al cargar) pero el total 2da de la guía tiene remanente exacto, asignarlo
            if rg_blocks and vol_2da_tot > 0:
                sum_blocks_2da = sum(b["2da"] for b in rg_blocks)
                rem_2da = round(vol_2da_tot - sum_blocks_2da, 4)
                if rem_2da > 0.01 and rg_blocks[-1]["2da"] == 0 and rg_blocks[-1]["1ra"] > 0:
                    rg_blocks[-1]["2da"] = rem_2da

            oc_raw = str(self.oc_compra or self.oc or "")
            matched_b = None
            matched_dp = None
            matched_dps = []

            if gcs.detalles_proceso and candidate_oc_ids:
                is_sd = "SD" in oc_raw.upper()
                is_bs = "BS" in oc_raw.upper()
                exact_dps = []
                fallback_dps = []
                for dp in gcs.detalles_proceso:
                    dp_oc = str(dp.oc_compra_entrada or "")
                    if any(str(cid) in dp_oc for cid in candidate_oc_ids):
                        dp_sd = "SD" in dp_oc.upper()
                        dp_bs = "BS" in dp_oc.upper()
                        if (is_sd and dp_sd) or (is_bs and dp_bs) or (not is_sd and not is_bs and not dp_sd and not dp_bs):
                            exact_dps.append(dp)
                        else:
                            fallback_dps.append(dp)
                matched_dps = exact_dps if exact_dps else fallback_dps
                if not matched_dps and len(gcs.detalles_proceso) == 1:
                    matched_dps = [gcs.detalles_proceso[0]]
                if matched_dps:
                    matched_dp = matched_dps[0]

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

            dp_sum_in = sum(float(d.volumen_m3_entrada or 0) for d in matched_dps) if matched_dps else 0.0
            dp_sum_out = sum(float(d.volumen_m3_salida or 0) for d in matched_dps) if matched_dps else 0.0

            if matched_b and (matched_b["1ra"] + matched_b["2da"]) > 0:
                if matched_b["in"] > 0:
                    vol_in = dp_sum_in if (dp_sum_in > 0 and abs(dp_sum_in - matched_b["in"]) < 0.05) else matched_b["in"]
                    vol_out = matched_b["1ra"] + matched_b["2da"]
                    vol_out_1ra = matched_b["1ra"]
                    vol_out_2da = matched_b["2da"]
                else:
                    # Madera viene ya cepillada (sin entrada rústica registrada en resumen_general)
                    dp_vol_cand = dp_sum_in if dp_sum_in > 0 else dp_sum_out

                    sum_salida = matched_b["1ra"] + matched_b["2da"]
                    if dp_vol_cand > 0 and sum_salida > 0:
                        vol_in = dp_vol_cand
                        vol_out = sum_salida
                        vol_out_1ra = matched_b["1ra"]
                        vol_out_2da = matched_b["2da"]
                    else:
                        # Si no hay entrada registrada ni merma, la madera ya cepillada entra y sale 1 a 1 (sin merma)
                        vol_in = 1.0
                        vol_out = 1.0
                        vol_out_1ra = matched_b["1ra"]
                        vol_out_2da = matched_b["2da"]
            else:
                # Match en detalles_proceso de GCS
                if dp_sum_in > 0:
                    vol_in = dp_sum_in
                    if len(gcs.detalles_proceso) == len(matched_dps) and total_vol_salida_gcs > 0:
                        vol_out = total_vol_salida_gcs
                    elif dp_sum_out > 0:
                        sum_dp_out = sum(float(dp.volumen_m3_salida or 0) for dp in gcs.detalles_proceso)
                        if sum_dp_out > 0 and total_vol_salida_gcs > 0:
                            vol_out = (dp_sum_out / sum_dp_out) * total_vol_salida_gcs
                        else:
                            vol_out = dp_sum_out
                elif total_vol_salida_gcs > 0:
                    vol_out = total_vol_salida_gcs

            # Safety fallback: si por alguna razón vol_out quedó en <= 0 o con un ratio irreal
            if vol_out <= 0 or (vol_in / vol_out > 5.0) or (vol_in > 0 and vol_out > 0 and (vol_in / vol_out < 0.2)):
                vol_in = 1.0
                vol_out = 1.0

        # 3. Costo Madera ($/m3) y Costo Madera Real ($/m3):
        # - costo_madera_m3: Costo de madera de compra / salida de proceso en planta (GCS: vol_in / vol_out)
        # - costo_madera_real_m3: Costo efectivo real de la madera ajustado por la variación entre Volumen Entrada y Volumen Real recibido en puerto
        costo_madera_m3 = round((vol_in * costo_compra_m3) / vol_out, 2) if (vol_out and vol_out > 0) else round(costo_compra_m3, 2)

        if vol_entrada and vol_real and vol_entrada > 0 and vol_real > 0 and abs(vol_entrada - vol_real) > 0.0001:
            base_madera_unrounded = ((vol_in * costo_compra_m3) / vol_out) if (vol_out and vol_out > 0) else costo_compra_m3
            costo_madera_real_m3 = round(base_madera_unrounded * (vol_entrada / vol_real), 2)
        else:
            costo_madera_real_m3 = costo_madera_m3

        # 3.1 Servicios Planta ($/m3) diferenciados por sub-lote / proceso (tarifa base directa sin factor de rendimiento)
        if gcs and (gcs.detalles or gcs.detalles_proceso):
            explicit_proc_weighted = 0.0
            explicit_proc_vol = 0.0
            has_explicit_proc = False
            if matched_dps:
                for d_proc in matched_dps:
                    proc_u = str(d_proc.proceso or "").upper()
                    if "CEPILLADO" in proc_u or "TROZADO" in proc_u:
                        has_explicit_proc = True
                        m_cep = re.search(r"CEPILLADO\s*\(\s*\$?([\d.,]+)\s*\)", proc_u)
                        m_troz = re.search(r"TROZADO\s*\(\s*\$?([\d.,]+)\s*\)", proc_u)
                        t_cep_dp = float(m_cep.group(1).replace(",", ".")) if m_cep else 0.0
                        t_troz_dp = float(m_troz.group(1).replace(",", ".")) if m_troz else 0.0
                        w_dp = float(d_proc.volumen_m3_salida or d_proc.volumen_m3_entrada or 1.0)
                        explicit_proc_weighted += w_dp * (t_cep_dp + t_troz_dp)
                        explicit_proc_vol += w_dp

            if has_explicit_proc and explicit_proc_vol > 0:
                servicios_m3 = round(explicit_proc_weighted / explicit_proc_vol, 2)
            elif gcs.detalles:
                tiene_cepillado = False
                if matched_dps:
                    for d_proc in matched_dps:
                        e_in = float(d_proc.espesor_entrada or 0)
                        a_in = float(d_proc.ancho_entrada or 0)
                        e_out = float(d_proc.espesor_salida or 0)
                        a_out = float(d_proc.ancho_salida or 0)
                        if (e_in > e_out + 0.5) or (a_in > a_out + 0.5):
                            tiene_cepillado = True
                            break
                elif matched_b and matched_b.get("in", 0) > 0:
                    tiene_cepillado = True

                item_dim_str = f"{int(float(self.espesor or 0))}X{int(float(self.ancho or 0))}"
                trozado_det = None
                cepillado_det = None

                for d in gcs.detalles:
                    s_name = str(d.servicio or "").upper()
                    if "TROZAD" in s_name:
                        if item_dim_str in s_name:
                            trozado_det = d
                        elif float(d.volumen_m3 or 0) > 0 and (not trozado_det or float(trozado_det.volumen_m3 or 0) <= 0):
                            trozado_det = d
                        elif not trozado_det:
                            trozado_det = d
                    elif "CEPILLAD" in s_name:
                        if float(d.volumen_m3 or 0) > 0 or not cepillado_det:
                            cepillado_det = d

                serv_item = 0.0
                # Tarifa directa de Trozado (sin multiplicar por factor de rendimiento)
                if trozado_det and trozado_det.tarifa_usd_m3:
                    t_troz = float(trozado_det.tarifa_usd_m3)
                    serv_item += t_troz

                # Tarifa directa de Cepillado (sin multiplicar por factor de rendimiento)
                if tiene_cepillado and cepillado_det and cepillado_det.tarifa_usd_m3:
                    t_cep = float(cepillado_det.tarifa_usd_m3)
                    serv_item += t_cep

                if serv_item > 0:
                    servicios_m3 = round(serv_item, 2)

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
            os_by_oc_cache = sess.info.setdefault("_os_by_oc_cache", {})
            if self.id_orden_compra not in os_by_oc_cache:
                os_by_oc_cache[self.id_orden_compra] = sess.query(OrdenServicio).filter(OrdenServicio.id_orden_compra == self.id_orden_compra).first()
            os_obj = os_by_oc_cache[self.id_orden_compra]
        if not os_obj and g and g.id_orden_compra and sess:
            from app.models.orden_servicio import OrdenServicio
            os_by_oc_cache = sess.info.setdefault("_os_by_oc_cache", {})
            if g.id_orden_compra not in os_by_oc_cache:
                os_by_oc_cache[g.id_orden_compra] = sess.query(OrdenServicio).filter(OrdenServicio.id_orden_compra == g.id_orden_compra).first()
            os_obj = os_by_oc_cache[g.id_orden_compra]

        flete_m3 = 0.0
        tiene_os = False
        id_os_linked = self.id_orden_servicio
        if os_obj:
            tiene_os = True
            id_os_linked = os_obj.id_orden_servicio
            if os_obj.flete:
                flete_total = float(os_obj.flete)
                # El flete de transporte corresponde a la carga real trasladada a puerto en la guía
                vol_transporte = 0.0
                if g and g.detalles:
                    vol_transporte = sum(
                        float(it.volumen_real if it.volumen_real is not None else (it.volumen_eq or it.volumen or 0))
                        for it in g.detalles
                    )
                if vol_transporte <= 0 and vol_1ra_tot > 0:
                    vol_transporte = vol_1ra_tot
                if vol_transporte <= 0:
                    vol_transporte = vol_real or 1.0

                flete_m3 = round(flete_total / vol_transporte, 2)

        # 5. Costo Final (Unitario y Totales sobre el Volumen Real llegado a puerto)
        # Formula: Costo Madera Real + Servicios + Flete
        costo_final_unitario = round(costo_madera_real_m3 + servicios_m3 + flete_m3, 2)
        vol_item = vol_real or 0.0
        costo_final_total = round(vol_item * costo_final_unitario, 2)
        costo_madera_total = round(vol_item * costo_madera_real_m3, 2)
        costo_servicios_total = round(vol_item * servicios_m3, 2)
        costo_flete_total = round(vol_item * flete_m3, 2)
        calc_sub = costo_madera_total

        # 6. Precio Venta Proforma y Rentabilidad / Utilidad Real en Puerto
        id_proforma_venta = None
        oe_numero = None
        precio_venta_m3 = None
        precio_venta_unitario = None
        venta_total_usd = None
        utilidad_m3 = None
        utilidad_total = None
        rentabilidad_pct = None
        rentabilidad_costo_pct = None

        if sess:
            from app.models.orden_compra import OrdenCompra
            from app.models.proforma import Proforma
            from app.models.detalle_proforma import DetalleProforma

            oc_obj_cache = sess.info.setdefault("_oc_obj_cache", {})
            pf_obj_cache = sess.info.setdefault("_pf_obj_cache", {})
            pf_by_oe_cache = sess.info.setdefault("_pf_by_oe_cache", {})
            pf_dets_cache = sess.info.setdefault("_pf_dets_cache", {})

            def _get_oc_obj(cid):
                if not cid:
                    return None
                if cid not in oc_obj_cache:
                    oc_obj_cache[cid] = sess.get(OrdenCompra, cid)
                return oc_obj_cache[cid]

            def _get_pf_obj(pid):
                if not pid:
                    return None
                if pid not in pf_obj_cache:
                    pf_obj_cache[pid] = sess.get(Proforma, pid)
                return pf_obj_cache[pid]

            def _get_pf_by_oe(oe_num):
                if not oe_num:
                    return None
                if oe_num not in pf_by_oe_cache:
                    pf_by_oe_cache[oe_num] = sess.query(Proforma).filter(Proforma.id_operacion_exportacion == oe_num).first()
                return pf_by_oe_cache[oe_num]

            pf_target = None
            # A) Directo desde id_orden_compra de item, guía u OS
            for direct_oc_id in [
                self.id_orden_compra,
                (g.id_orden_compra if g else None),
                (os_obj.id_orden_compra if os_obj else None),
            ]:
                if direct_oc_id:
                    oc_cand = _get_oc_obj(direct_oc_id)
                    if oc_cand and oc_cand.id_proforma:
                        pf_target = _get_pf_obj(oc_cand.id_proforma)
                        if pf_target:
                            break

            # B) Desde los números en el campo oc (ej: "8160-8083" -> OE 8160 o OC 8083)
            if not pf_target:
                oc_nums = []
                for raw_oc_str in [self.oc, (g.oc if g else None)]:
                    if raw_oc_str:
                        for ns in re.findall(r"\d+", str(raw_oc_str)):
                            ni = int(ns)
                            if ni not in oc_nums:
                                oc_nums.append(ni)
                for ni in oc_nums:
                    oc_cand = _get_oc_obj(ni)
                    if oc_cand and oc_cand.id_proforma:
                        pf_target = _get_pf_obj(oc_cand.id_proforma)
                        if pf_target:
                            break
                    pf_cand = _get_pf_by_oe(ni)
                    if pf_cand:
                        pf_target = pf_cand
                        break
                    pf_cand2 = _get_pf_obj(ni)
                    if pf_cand2:
                        pf_target = pf_cand2
                        break

            if pf_target:
                id_proforma_venta = pf_target.id_proforma
                oe_numero = pf_target.id_operacion_exportacion
                if id_proforma_venta not in pf_dets_cache:
                    pf_dets_cache[id_proforma_venta] = (
                        sess.query(DetalleProforma)
                        .filter(DetalleProforma.id_proforma == id_proforma_venta)
                        .all()
                    )
                pf_dets = pf_dets_cache[id_proforma_venta]
                dp_match = None
                if pf_dets:
                    exact_dp = [
                        dp for dp in pf_dets
                        if _dim_eq(dp.espesor, esp_real)
                        and _dim_eq(dp.ancho, anc_real)
                        and _dim_eq(dp.largo, lar_real)
                    ]
                    if exact_dp:
                        dp_match = exact_dp[0]
                    else:
                        ea_dp = [
                            dp for dp in pf_dets
                            if _dim_eq(dp.espesor, esp_real) and _dim_eq(dp.ancho, anc_real)
                        ]
                        if ea_dp:
                            dp_match = ea_dp[0]
                        else:
                            prod_dp = [dp for dp in pf_dets if self.id_producto and dp.id_producto == self.id_producto]
                            dp_match = prod_dp[0] if prod_dp else pf_dets[0]

                if dp_match:
                    if dp_match.precio_eq is not None and float(dp_match.precio_eq) > 0:
                        precio_venta_m3 = round(float(dp_match.precio_eq), 2)
                    elif dp_match.subtotal and dp_match.volumen_eq and float(dp_match.volumen_eq) > 0:
                        precio_venta_m3 = round(float(dp_match.subtotal) / float(dp_match.volumen_eq), 2)
                    elif dp_match.precio_unitario is not None and float(dp_match.precio_unitario) > 0:
                        precio_venta_m3 = round(float(dp_match.precio_unitario), 2)

                    if dp_match.precio_unitario is not None and float(dp_match.precio_unitario) > 0:
                        precio_venta_unitario = round(float(dp_match.precio_unitario), 4)

        if precio_venta_m3 is not None and precio_venta_m3 > 0:
            venta_total_usd = round(vol_item * precio_venta_m3, 2)
            utilidad_m3 = round(precio_venta_m3 - costo_final_unitario, 2)
            utilidad_total = round(venta_total_usd - costo_final_total, 2)
            rentabilidad_pct = round((utilidad_total / venta_total_usd) * 100, 2) if venta_total_usd > 0 else 0.0
            rentabilidad_costo_pct = round((utilidad_total / costo_final_total) * 100, 2) if costo_final_total > 0 else 0.0

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
            "cantidad": _num(self.cantidad) if self.cantidad is not None else vol_real,
            "espesor": esp_real,
            "id_unidad_medida_espesor": self.id_unidad_medida_espesor,
            "ancho": anc_real,
            "id_unidad_medida_ancho": self.id_unidad_medida_ancho,
            "largo": lar_real,
            "id_unidad_medida_largo": self.id_unidad_medida_largo,
            "espesor_entrada": esp_entrada,
            "ancho_entrada": anc_entrada,
            "largo_entrada": lar_entrada,
            "piezas_entrada": pzs_entrada,
            "volumen_entrada": vol_entrada,
            "espesor_real": esp_real,
            "ancho_real": anc_real,
            "largo_real": lar_real,
            "piezas_real": pzs_real,
            "volumen_real": vol_real,
            "precio_unitario": calc_pu,
            "subtotal": calc_sub,
            "volumen": vol_entrada if vol_entrada is not None else _num(self.volumen),
            "volumen_eq": vol_real if vol_real is not None else _num(self.volumen_eq),
            "precio_eq": calc_peq,
            "piezas": pzs_real if pzs_real is not None else _num(self.piezas),
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
            "volumen_salida_1ra": round(vol_out_1ra, 4) if vol_out_1ra > 0 else None,
            "volumen_salida_2da": round(vol_out_2da, 4) if vol_out_2da > 0 else None,
            "volumen_salida_1ra_guia": round(vol_1ra_tot, 4) if vol_1ra_tot > 0 else None,
            "volumen_salida_2da_guia": round(vol_2da_tot, 4) if vol_2da_tot > 0 else None,
            "volumen_total_salida_gcs": round(total_vol_salida_gcs, 4) if total_vol_salida_gcs > 0 else None,
            "costo_madera_m3": costo_madera_m3,
            "costo_madera_real_m3": costo_madera_real_m3,
            "servicios_m3": servicios_m3,
            "flete_m3": flete_m3,
            "costo_final_unitario": costo_final_unitario,
            "costo_final_total": costo_final_total,
            "costo_madera_total": costo_madera_total,
            "costo_servicios_total": costo_servicios_total,
            "costo_flete_total": costo_flete_total,
            "tiene_orden_servicio": tiene_os,
            "id_proforma_venta": id_proforma_venta,
            "oe_numero": oe_numero,
            "precio_venta_m3": precio_venta_m3,
            "precio_venta_unitario": precio_venta_unitario,
            "venta_total_usd": venta_total_usd,
            "utilidad_m3": utilidad_m3,
            "utilidad_total": utilidad_total,
            "rentabilidad_pct": rentabilidad_pct,
            "rentabilidad_costo_pct": rentabilidad_costo_pct,
        }
