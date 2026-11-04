from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import date


class GuiaInventarioPuerto(Base):
    __tablename__ = "guia_inventario_puerto"

    id_guia_inventario_puerto = Column(Integer, primary_key=True, autoincrement=True)

    numero_guia = Column(String(100), nullable=True, index=True)
    oc = Column(String(100), nullable=True)
    origen = Column(String(100), nullable=True)
    id_orden_servicio = Column(Integer, ForeignKey("orden_servicio.id_orden_servicio"), nullable=True)
    id_orden_compra = Column(Integer, ForeignKey("orden_compra.id_orden_compra"), nullable=True)
    id_bodega = Column(Integer, ForeignKey("bodega.id_bodega"), nullable=True)
    fecha_recepcion = Column(Date, default=date.today)
    url_documento = Column(String(500), nullable=True)
    observaciones = Column(String(500), nullable=True)
    estado = Column(String(50), default="RECIBIDO")

    # Relaciones viewonly / ORM
    OrdenServicio = relationship(
        "OrdenServicio",
        primaryjoin="foreign(GuiaInventarioPuerto.id_orden_servicio)==OrdenServicio.id_orden_servicio",
        viewonly=True,
    )
    OrdenCompra = relationship(
        "OrdenCompra",
        primaryjoin="foreign(GuiaInventarioPuerto.id_orden_compra)==OrdenCompra.id_orden_compra",
        viewonly=True,
    )
    Bodega = relationship(
        "Bodega",
        primaryjoin="foreign(GuiaInventarioPuerto.id_bodega)==Bodega.id_bodega",
        viewonly=True,
    )
    detalles = relationship(
        "InventarioPuerto",
        back_populates="guia",
        cascade="all, delete-orphan",
        order_by="InventarioPuerto.id_inventario_puerto",
    )

    def __repr__(self):
        return f"<GuiaInventarioPuerto {self.id_guia_inventario_puerto} - Guia {self.numero_guia}>"

    def to_dict(self):
        from sqlalchemy.orm import object_session
        sess = object_session(self)

        bodega = self.__dict__.get("Bodega")
        if not bodega and self.id_bodega and sess:
            from app.models.bodega import Bodega
            bodega = sess.get(Bodega, self.id_bodega)
        elif not bodega:
            bodega = self.Bodega
        bodega_nombre = getattr(bodega, "nombre", None) if bodega else None

        proveedor_nombre = None
        os_rel = self.__dict__.get("OrdenServicio")
        if not os_rel and self.id_orden_servicio and sess:
            from app.models.orden_servicio import OrdenServicio
            os_rel = sess.get(OrdenServicio, self.id_orden_servicio)
        elif not os_rel:
            os_rel = self.OrdenServicio

        if os_rel and getattr(os_rel, "id_cliente_proveedor", None) and sess:
            from app.models.cliente_proveedor import ClienteProveedor
            cp = sess.get(ClienteProveedor, os_rel.id_cliente_proveedor)
            if cp:
                proveedor_nombre = getattr(cp, "razon_social", None)
        elif os_rel and getattr(os_rel, "ClienteProveedor", None):
            proveedor_nombre = getattr(os_rel.ClienteProveedor, "razon_social", None)
        else:
            oc_rel = self.__dict__.get("OrdenCompra")
            if not oc_rel and self.id_orden_compra and sess:
                from app.models.orden_compra import OrdenCompra
                oc_rel = sess.get(OrdenCompra, self.id_orden_compra)
            elif not oc_rel:
                oc_rel = self.OrdenCompra
            if oc_rel and getattr(oc_rel, "id_cliente_proveedor", None) and sess:
                from app.models.cliente_proveedor import ClienteProveedor
                cp = sess.get(ClienteProveedor, oc_rel.id_cliente_proveedor)
                if cp:
                    proveedor_nombre = getattr(cp, "razon_social", None)
            elif oc_rel and getattr(oc_rel, "ClienteProveedor", None):
                proveedor_nombre = getattr(oc_rel.ClienteProveedor, "razon_social", None)

        if self.detalles and sess:
            import re
            from app.models.detalle_orden_compra import DetalleOrdenCompra
            odc_dets_cache = sess.info.setdefault("_odc_dets_cache", {})
            batch_cids = set()
            for d_item in self.detalles:
                d_item.__dict__["guia"] = self
                if d_item.id_orden_compra:
                    batch_cids.add(d_item.id_orden_compra)
                for raw_oc in (d_item.oc_compra, d_item.oc, self.oc):
                    if raw_oc:
                        for n_s in re.findall(r"\d+", str(raw_oc)):
                            batch_cids.add(int(n_s))
            missing_cids = [cid for cid in batch_cids if cid not in odc_dets_cache]
            if missing_cids:
                fetched_dets = sess.query(DetalleOrdenCompra).filter(DetalleOrdenCompra.id_orden_compra.in_(missing_cids)).all()
                for cid in missing_cids:
                    odc_dets_cache[cid] = []
                for fd in fetched_dets:
                    odc_dets_cache.setdefault(fd.id_orden_compra, []).append(fd)

        detalles_list = [d.to_dict() for d in self.detalles] if self.detalles else []
        total_volumen = sum(d.get("volumen_eq") or d.get("volumen") or 0 for d in detalles_list)
        total_piezas = sum(d.get("piezas") or 0 for d in detalles_list)
        total_paquetes = sum(d.get("numero_paquetes") or 0 for d in detalles_list)

        total_costo_madera = sum(d.get("costo_madera_total") or d.get("subtotal") or 0 for d in detalles_list)
        total_servicios = sum(d.get("costo_servicios_total") or 0 for d in detalles_list)
        total_flete = sum(d.get("costo_flete_total") or 0 for d in detalles_list)
        total_costo_final = sum(d.get("costo_final_total") or 0 for d in detalles_list)
        costo_final_promedio_m3 = round(total_costo_final / total_volumen, 2) if total_volumen > 0 else 0.0

        servicios_m3 = round(total_servicios / total_volumen, 2) if total_volumen > 0 else (detalles_list[0].get("servicios_m3", 0.0) if detalles_list else 0.0)
        flete_m3 = detalles_list[0].get("flete_m3", 0.0) if detalles_list else 0.0
        tiene_os = any(d.get("tiene_orden_servicio") for d in detalles_list)
        id_os = self.id_orden_servicio or (detalles_list[0].get("id_orden_servicio") if detalles_list else None)

        from sqlalchemy.orm import object_session
        sess = object_session(self)
        os_flete_val = None
        if id_os and sess:
            from app.models.orden_servicio import OrdenServicio
            os_rec = sess.get(OrdenServicio, id_os)
            if os_rec and os_rec.flete is not None:
                os_flete_val = float(os_rec.flete)

        if os_flete_val is not None:
            total_flete = round(os_flete_val, 2)
            if total_volumen > 0:
                flete_m3 = round(total_flete / total_volumen, 2)
            if detalles_list and total_volumen > 0:
                cur_sum = 0.0
                for d in detalles_list:
                    it_vol = float(d.get("volumen_eq") or d.get("volumen") or 0.0)
                    it_flete = round((it_vol / total_volumen) * total_flete, 2)
                    d["costo_flete_total"] = it_flete
                    cur_sum += it_flete
                diff = round(total_flete - cur_sum, 2)
                if diff != 0.0:
                    detalles_list[-1]["costo_flete_total"] = round(detalles_list[-1]["costo_flete_total"] + diff, 2)
                for d in detalles_list:
                    d["flete_m3"] = flete_m3
                    d["costo_final_unitario"] = round(float(d.get("costo_madera_m3") or 0) + float(d.get("servicios_m3") or 0) + flete_m3, 2)
                    d["costo_final_total"] = round(float(d.get("costo_madera_total") or 0) + float(d.get("costo_servicios_total") or 0) + float(d.get("costo_flete_total") or 0), 2)

        total_costo_final = sum(d.get("costo_final_total") or 0 for d in detalles_list)
        costo_final_promedio_m3 = round(total_costo_final / total_volumen, 2) if total_volumen > 0 else 0.0
        vol_salida_1ra_guia = detalles_list[0].get("volumen_salida_1ra_guia") if detalles_list else None
        vol_salida_2da_guia = detalles_list[0].get("volumen_salida_2da_guia") if detalles_list else None
        vol_total_salida_gcs = detalles_list[0].get("volumen_total_salida_gcs") if detalles_list else None

        return {
            "id_guia_inventario_puerto": self.id_guia_inventario_puerto,
            "numero_guia": self.numero_guia,
            "oc": self.oc,
            "origen": self.origen,
            "id_orden_servicio": id_os,
            "id_orden_compra": self.id_orden_compra,
            "id_bodega": self.id_bodega,
            "bodega_nombre": bodega_nombre,
            "proveedor_nombre": proveedor_nombre,
            "fecha_recepcion": self.fecha_recepcion.isoformat() if self.fecha_recepcion else None,
            "url_documento": self.url_documento,
            "observaciones": self.observaciones,
            "estado": self.estado,
            "total_volumen": round(total_volumen, 3),
            "total_piezas": total_piezas,
            "total_paquetes": total_paquetes,
            "total_costo_madera": round(total_costo_madera, 2),
            "total_servicios": round(total_servicios, 2),
            "total_flete": round(total_flete, 2),
            "total_costo_final": round(total_costo_final, 2),
            "costo_final_promedio_m3": costo_final_promedio_m3,
            "servicios_m3": servicios_m3,
            "flete_m3": flete_m3,
            "tiene_orden_servicio": tiene_os,
            "volumen_salida_1ra": vol_salida_1ra_guia,
            "volumen_salida_2da": vol_salida_2da_guia,
            "volumen_total_salida_gcs": vol_total_salida_gcs,
            "detalles": detalles_list,
        }

