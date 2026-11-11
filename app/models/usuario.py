from sqlalchemy import Column, Integer, String, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.seguridad import Seguridad

# Catálogo oficial de módulos del sistema agrupados por categoría
SYSTEM_MODULES_CATALOG = [
    # Comercial y Exportación
    {"modulo": "PROFORMA", "nombre": "Proformas", "categoria": "Comercial y Exportación", "descripcion": "Creación, edición, PDF y seguimiento de proformas"},
    {"modulo": "EXPORTACION", "nombre": "Operaciones de Exportación", "categoria": "Comercial y Exportación", "descripcion": "Gestión de operaciones de exportación (OE) y embarques"},
    # Compras y Abastecimiento
    {"modulo": "ORDEN_COMPRA", "nombre": "Órdenes de Compra", "categoria": "Compras y Abastecimiento", "descripcion": "Gestión de órdenes de compra directas y asociadas a proforma"},
    # Inventarios
    {"modulo": "INVENTARIO_DASHBOARD", "nombre": "Dashboard de Inventario", "categoria": "Inventarios", "descripcion": "Visualización ejecutiva de m³ y valorización de inventarios"},
    {"modulo": "INVENTARIO_TRANSITORIO", "nombre": "Inventario Transitorio", "categoria": "Inventarios", "descripcion": "Recepción de OC, guías de despacho y control de saldos en tránsito"},
    {"modulo": "INVENTARIO_PUERTO", "nombre": "Inventario Puerto", "categoria": "Inventarios", "descripcion": "Recepción de OS en puerto, cubicación real y cálculo de costo final"},
    {"modulo": "INVENTARIO_SEGUNDA", "nombre": "Inventario de Segunda", "categoria": "Inventarios", "descripcion": "Control de stock y guías de productos de segunda"},
    # Servicios
    {"modulo": "SERVICIOS_DASHBOARD", "nombre": "Dashboard Costos de Servicio", "categoria": "Servicios", "descripcion": "Indicadores y análisis de costos de servicio"},
    {"modulo": "ORDEN_SERVICIO", "nombre": "Órdenes de Servicio", "categoria": "Servicios", "descripcion": "Emisión y gestión de órdenes de servicio a planta/bodega"},
    {"modulo": "GUIA_COSTO_SERVICIO", "nombre": "Guías de Costo de Servicio", "categoria": "Servicios", "descripcion": "Carga de Excel Detalle Servicio y recepción de guías de costo"},
    # Administración y Seguridad
    {"modulo": "USUARIO", "nombre": "Usuarios, Roles y Permisos", "categoria": "Administración y Seguridad", "descripcion": "Administración de cuentas de usuario, roles y matriz de acceso"},
    # Mantenedores
    {"modulo": "EMPRESA", "nombre": "Empresas", "categoria": "Mantenedores", "descripcion": "Mantenedor de empresas emisoras del grupo"},
    {"modulo": "CLIENTE_PROVEEDOR", "nombre": "Clientes y Proveedores", "categoria": "Mantenedores", "descripcion": "Mantenedor de clientes, proveedores, contactos y direcciones"},
    {"modulo": "PRODUCTO", "nombre": "Detalle de Productos", "categoria": "Mantenedores", "descripcion": "Mantenedor de productos, especies y clases"},
    {"modulo": "UNIDAD_VENTA", "nombre": "Unidades de Venta", "categoria": "Mantenedores", "descripcion": "Mantenedor de unidades de venta y cubicación"},
    {"modulo": "UNIDAD_MEDIDA", "nombre": "Unidades de Medida", "categoria": "Mantenedores", "descripcion": "Mantenedor de unidades de medida"},
    {"modulo": "TIPO_COMISION", "nombre": "Tipos de Comisión", "categoria": "Mantenedores", "descripcion": "Mantenedor de tipos de comisión comercial"},
    {"modulo": "AGENTE", "nombre": "Agentes", "categoria": "Mantenedores", "descripcion": "Mantenedor de agentes comerciales"},
    {"modulo": "BODEGA", "nombre": "Bodegas", "categoria": "Mantenedores", "descripcion": "Mantenedor de bodegas y plantas"},
    {"modulo": "UBICACION", "nombre": "Ubicaciones y Navieras", "categoria": "Mantenedores", "descripcion": "Mantenedor de países, ciudades, puertos y navieras"},
    {"modulo": "FINANCIERO", "nombre": "Financiero", "categoria": "Mantenedores", "descripcion": "Mantenedor de monedas, formas de pago, cláusulas de venta y gastos"},
    {"modulo": "CONTENEDOR", "nombre": "Contenedores y Envases", "categoria": "Mantenedores", "descripcion": "Mantenedor de tipos de contenedor y envase"},
]

SYSTEM_MODULES = tuple(item["modulo"] for item in SYSTEM_MODULES_CATALOG)

# Alias para compatibilidad con nombres históricos o de tablas individuales
MODULE_ALIASES = {
    "PROFORMAS": "PROFORMA",
    "DETALLE_PROFORMA": "PROFORMA",
    "CONTACTO_PROFORMA": "PROFORMA",
    "CONTACTO_PROF": "PROFORMA",
    "ESTADO_PROFORMA": "PROFORMA",
    "COMEX": "EXPORTACION",
    "OPER_EXPORT": "EXPORTACION",
    "OPERACION_EXPORTACION": "EXPORTACION",
    "ESTADO_OE": "EXPORTACION",
    "IDE": "EXPORTACION",
    "DETALLE_IDE": "EXPORTACION",
    "DOCUMENTO_IDE": "EXPORTACION",
    "FACTURA": "EXPORTACION",
    "DETALLE_FACTURA": "EXPORTACION",
    "PACKINGLIST": "EXPORTACION",
    "DETALLE_PL": "EXPORTACION",
    "ESTADO_PL": "EXPORTACION",
    "PLC": "EXPORTACION",
    "PLE": "EXPORTACION",
    "ESTADO_DET_PLE": "EXPORTACION",
    "ORDENCOMPRA": "ORDEN_COMPRA",
    "ORDENES_COMPRA": "ORDEN_COMPRA",
    "DETALLE_ORDEN_COMPRA": "ORDEN_COMPRA",
    "CONTACTO_ORDEN_COMPRA": "ORDEN_COMPRA",
    "CONTACTO_ODC": "ORDEN_COMPRA",
    "ESTADO_ODC": "ORDEN_COMPRA",
    "ORDENES_SERVICIO": "ORDEN_SERVICIO",
    "CONTACTO_ORDEN_SERVICIO": "ORDEN_SERVICIO",
    "ESTADO_ORDEN_SERVICIO": "ORDEN_SERVICIO",
    "GUIAS_COSTO_SERVICIO": "GUIA_COSTO_SERVICIO",
    "USUARIOS": "USUARIO",
    "SEGURIDAD": "USUARIO",
    "CLIENTE_PROV": "CLIENTE_PROVEEDOR",
    "CLIENTES": "CLIENTE_PROVEEDOR",
    "CONTACTO": "CLIENTE_PROVEEDOR",
    "DIRECCION": "CLIENTE_PROVEEDOR",
    "PRODUCTOS": "PRODUCTO",
    "ESPECIE": "PRODUCTO",
    "ESPECIES": "PRODUCTO",
    "CLASE": "PRODUCTO",
    "CLASES": "PRODUCTO",
    "UNIDADES_VENTA": "UNIDAD_VENTA",
    "UNIDADES_MEDIDA": "UNIDAD_MEDIDA",
    "TIPOS_COMISION": "TIPO_COMISION",
    "AGENTES": "AGENTE",
    "BODEGAS": "BODEGA",
    "UBICACIONES": "UBICACION",
    "PAIS": "UBICACION",
    "CIUDAD": "UBICACION",
    "PUERTO": "UBICACION",
    "NAVIERA": "UBICACION",
    "FINANCIEROS": "FINANCIERO",
    "MONEDA": "FINANCIERO",
    "FORMA_PAGO": "FINANCIERO",
    "CLAUSULA_VENTA": "FINANCIERO",
    "GASTO": "FINANCIERO",
    "DETALLE_GASTO": "FINANCIERO",
    "PARAMETRO": "FINANCIERO",
    "CONTENEDORES": "CONTENEDOR",
    "TIPO_ENVASE": "CONTENEDOR",
}

# Fallback jerárquico para usuarios existentes que tenían permisos por categoría general
MODULE_PARENT_FALLBACK = {
    "INVENTARIO_DASHBOARD": ("INVENTARIO", "INFORME", "INFORMES"),
    "INVENTARIO_TRANSITORIO": ("INVENTARIO",),
    "INVENTARIO_PUERTO": ("INVENTARIO",),
    "INVENTARIO_SEGUNDA": ("INVENTARIO",),
    "SERVICIOS_DASHBOARD": ("SERVICIOS", "INVENTARIO", "INFORME", "INFORMES"),
    "ORDEN_SERVICIO": ("SERVICIOS", "INVENTARIO"),
    "GUIA_COSTO_SERVICIO": ("SERVICIOS", "INVENTARIO"),
    "EMPRESA": ("MANTENEDORES",),
    "CLIENTE_PROVEEDOR": ("MANTENEDORES",),
    "PRODUCTO": ("MANTENEDORES",),
    "UNIDAD_VENTA": ("MANTENEDORES",),
    "UNIDAD_MEDIDA": ("MANTENEDORES",),
    "TIPO_COMISION": ("MANTENEDORES",),
    "AGENTE": ("MANTENEDORES",),
    "BODEGA": ("MANTENEDORES",),
    "UBICACION": ("MANTENEDORES",),
    "FINANCIERO": ("MANTENEDORES",),
    "CONTENEDOR": ("MANTENEDORES",),
}

MANTENEDOR_MODULES = (
    "EMPRESA",
    "CLIENTE_PROVEEDOR",
    "PRODUCTO",
    "UNIDAD_VENTA",
    "UNIDAD_MEDIDA",
    "TIPO_COMISION",
    "AGENTE",
    "BODEGA",
    "UBICACION",
    "FINANCIERO",
    "CONTENEDOR",
)


def _full_perm() -> dict:
    return {"ver": True, "crear": True, "editar": True, "eliminar": True}


def _read_perm() -> dict:
    return {"ver": True, "crear": False, "editar": False, "eliminar": False}


def _rw_no_delete_perm() -> dict:
    return {"ver": True, "crear": True, "editar": True, "eliminar": False}


def _none_perm() -> dict:
    return {"ver": False, "crear": False, "editar": False, "eliminar": False}


ROLE_TEMPLATES = {
    "ADMINISTRADOR": {
        "codigo": "ADMINISTRADOR",
        "nombre": "Administrador General",
        "descripcion": "Acceso total a todos los módulos operativos, inventarios, servicios, mantenedores y seguridad de usuarios.",
        "permisos": {m: _full_perm() for m in SYSTEM_MODULES},
    },
    "COMERCIAL": {
        "codigo": "COMERCIAL",
        "nombre": "Comercial / COMEX",
        "descripcion": "Gestión completa de Proformas, Exportaciones y Órdenes de Compra, con consulta de inventarios y gestión de catálogos comerciales.",
        "permisos": {
            **{m: _none_perm() for m in SYSTEM_MODULES},
            "PROFORMA": _full_perm(),
            "EXPORTACION": _full_perm(),
            "ORDEN_COMPRA": _full_perm(),
            "INVENTARIO_DASHBOARD": _read_perm(),
            "INVENTARIO_TRANSITORIO": _read_perm(),
            "INVENTARIO_PUERTO": _read_perm(),
            "INVENTARIO_SEGUNDA": _read_perm(),
            "SERVICIOS_DASHBOARD": _read_perm(),
            "ORDEN_SERVICIO": _read_perm(),
            "GUIA_COSTO_SERVICIO": _read_perm(),
            "EMPRESA": _read_perm(),
            "CLIENTE_PROVEEDOR": _rw_no_delete_perm(),
            "PRODUCTO": _rw_no_delete_perm(),
            "UNIDAD_VENTA": _read_perm(),
            "UNIDAD_MEDIDA": _read_perm(),
            "TIPO_COMISION": _read_perm(),
            "AGENTE": _rw_no_delete_perm(),
            "BODEGA": _read_perm(),
            "UBICACION": _rw_no_delete_perm(),
            "FINANCIERO": _read_perm(),
            "CONTENEDOR": _read_perm(),
        },
    },
    "OPERACIONES": {
        "codigo": "OPERACIONES",
        "nombre": "Operaciones e Inventario",
        "descripcion": "Gestión completa de Órdenes de Compra, Inventarios (Transitorio, Puerto, Segunda) y Servicios, con lectura de Proformas y Exportaciones.",
        "permisos": {
            **{m: _none_perm() for m in SYSTEM_MODULES},
            "PROFORMA": _read_perm(),
            "EXPORTACION": _read_perm(),
            "ORDEN_COMPRA": _full_perm(),
            "INVENTARIO_DASHBOARD": _full_perm(),
            "INVENTARIO_TRANSITORIO": _full_perm(),
            "INVENTARIO_PUERTO": _full_perm(),
            "INVENTARIO_SEGUNDA": _full_perm(),
            "SERVICIOS_DASHBOARD": _full_perm(),
            "ORDEN_SERVICIO": _full_perm(),
            "GUIA_COSTO_SERVICIO": _full_perm(),
            "CLIENTE_PROVEEDOR": _rw_no_delete_perm(),
            "PRODUCTO": _rw_no_delete_perm(),
            "BODEGA": _rw_no_delete_perm(),
            "UNIDAD_VENTA": _read_perm(),
            "UNIDAD_MEDIDA": _read_perm(),
            "UBICACION": _read_perm(),
            "CONTENEDOR": _read_perm(),
        },
    },
    "SERVICIOS": {
        "codigo": "SERVICIOS",
        "nombre": "Servicios y Planta",
        "descripcion": "Gestión de Órdenes de Servicio, Guías de Costo de Servicio y recepción en Inventarios asociados.",
        "permisos": {
            **{m: _none_perm() for m in SYSTEM_MODULES},
            "ORDEN_COMPRA": _read_perm(),
            "INVENTARIO_DASHBOARD": _read_perm(),
            "INVENTARIO_TRANSITORIO": _rw_no_delete_perm(),
            "INVENTARIO_PUERTO": _rw_no_delete_perm(),
            "INVENTARIO_SEGUNDA": _rw_no_delete_perm(),
            "SERVICIOS_DASHBOARD": _full_perm(),
            "ORDEN_SERVICIO": _full_perm(),
            "GUIA_COSTO_SERVICIO": _full_perm(),
            "CLIENTE_PROVEEDOR": _read_perm(),
            "PRODUCTO": _read_perm(),
            "BODEGA": _read_perm(),
            "UNIDAD_MEDIDA": _read_perm(),
        },
    },
    "LECTURA": {
        "codigo": "LECTURA",
        "nombre": "Solo Lectura / Consulta",
        "descripcion": "Acceso de visualización y consulta a los módulos operativos, dashboards y mantenedores sin permisos de modificación.",
        "permisos": {
            **{m: _read_perm() for m in SYSTEM_MODULES},
            "USUARIO": _none_perm(),
        },
    },
    "PERSONALIZADO": {
        "codigo": "PERSONALIZADO",
        "nombre": "Personalizado",
        "descripcion": "Permisos configurados manualmente a medida por módulo.",
        "permisos": {m: _none_perm() for m in SYSTEM_MODULES},
    },
}


def normalize_module_code(modulo: str) -> str:
    clean = (modulo or "").strip().upper()
    return MODULE_ALIASES.get(clean, clean)


class User(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True, index=True)
    rut = Column(String(20), unique=True, nullable=True)
    nombre = Column(String(120), nullable=False)
    login = Column(String(80), unique=True, index=True, nullable=False)
    pass_ = Column("pass", String(255), nullable=False)
    correo = Column(String(200), unique=True, index=True, nullable=False)
    telefono = Column(String(50), nullable=True)
    url_firma = Column(String(255), nullable=True)
    rol = Column(String(50), nullable=False, default="PERSONALIZADO", server_default="PERSONALIZADO")
    activo = Column(Boolean, default=True, nullable=False)

    __table_args__ = (UniqueConstraint("login", name="uq_usuario_login"),)

    seguridades = relationship("Seguridad", back_populates="usuario", lazy="selectin", cascade="all, delete-orphan")

    # Convenience property expected by some auth code
    @property
    def hashed_password(self) -> str:
        return self.pass_

    @property
    def nombre_capitalizado(self) -> str:
        """Retorna el nombre con la primera letra de cada palabra en mayúscula"""
        return self.nombre.title() if self.nombre else ""

    def set_password(self, raw_password: str):
        if raw_password is None:
            raise ValueError("La contraseña no puede ser None")
        raw_password = str(raw_password)
        if raw_password == "":
            raise ValueError("La contraseña no puede ser vacía")
        from app.core.security import get_password_hash
        self.pass_ = get_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        if not self.pass_:
            return False
        try:
            from app.core.security import verify_password
            ok, _ = verify_password(raw_password or "", self.pass_)
            return ok
        except Exception:
            return False

    def is_admin_user(self) -> bool:
        login_clean = (self.login or "").strip().lower()
        rol_clean = (self.rol or "").strip().upper()
        if rol_clean == "ADMINISTRADOR" or login_clean in ("admin", "administrador"):
            return True
        return False

    def __repr__(self):
        return f"<User id={self.id_usuario} login={self.login} rol={self.rol} activo={self.activo}>"

    def to_dict(self) -> dict:
        raw_by_mod: dict[str, dict] = {}
        permisos_by_mod: dict[str, dict] = {}
        seguridades = self.seguridades or []
        seguridades_response = []

        # 1. Cargar permisos explícitos desde la base de datos
        for s in seguridades:
            raw_mod = (s.modulo or "").strip().upper()
            if not raw_mod:
                continue

            id_seguridad = getattr(s, "id_seguridad", 0) or 0
            entry = {
                "id_seguridad": id_seguridad,
                "crear": bool(s.crear),
                "ver": bool(s.ver),
                "editar": bool(s.editar),
                "eliminar": bool(s.eliminar),
            }
            raw_by_mod[raw_mod] = entry

            canonical_mod = normalize_module_code(raw_mod)
            if canonical_mod in permisos_by_mod:
                # Combinar con OR si hay alias heredados duplicados (ej. SEGURIDAD y USUARIO)
                existing = permisos_by_mod[canonical_mod]
                permisos_by_mod[canonical_mod] = {
                    "id_seguridad": existing["id_seguridad"] or id_seguridad,
                    "crear": existing["crear"] or entry["crear"],
                    "ver": existing["ver"] or entry["ver"],
                    "editar": existing["editar"] or entry["editar"],
                    "eliminar": existing["eliminar"] or entry["eliminar"],
                }
            else:
                permisos_by_mod[canonical_mod] = dict(entry)

            seg_dict = s.to_dict()
            seg_dict["modulo"] = canonical_mod
            seguridades_response.append(seg_dict)

        # Determinar rol efectivo
        rol_value = (getattr(self, "rol", None) or "").strip().upper()
        login_clean = (self.login or "").strip().lower()
        if not rol_value or rol_value == "PERSONALIZADO":
            if login_clean in ("admin", "administrador"):
                rol_value = "ADMINISTRADOR"
            elif permisos_by_mod.get("USUARIO", {}).get("crear") and permisos_by_mod.get("USUARIO", {}).get("editar"):
                rol_value = "ADMINISTRADOR"
            elif not rol_value:
                rol_value = "PERSONALIZADO"

        is_admin = rol_value == "ADMINISTRADOR" or login_clean in ("admin", "administrador")

        # 2. Completar todos los módulos canónicos del sistema
        for modulo in SYSTEM_MODULES:
            if is_admin:
                existing_id = permisos_by_mod.get(modulo, {}).get("id_seguridad", 0)
                permisos_by_mod[modulo] = {
                    "id_seguridad": existing_id,
                    "crear": True,
                    "ver": True,
                    "editar": True,
                    "eliminar": True,
                }
            elif modulo not in permisos_by_mod:
                # Revisar si existe permiso heredado en categoría padre (compatibilidad con registros antiguos)
                inherited = None
                for parent_code in MODULE_PARENT_FALLBACK.get(modulo, ()):
                    if parent_code in raw_by_mod:
                        inherited = raw_by_mod[parent_code]
                        break
                if inherited:
                    permisos_by_mod[modulo] = {
                        "id_seguridad": 0,
                        "crear": bool(inherited["crear"]),
                        "ver": bool(inherited["ver"]),
                        "editar": bool(inherited["editar"]),
                        "eliminar": bool(inherited["eliminar"]),
                    }
                else:
                    permisos_by_mod[modulo] = {
                        "id_seguridad": 0,
                        "crear": False,
                        "ver": False,
                        "editar": False,
                        "eliminar": False,
                    }

        # Sincronizar seguridades_response con el mapa consolidado de módulos del sistema
        seguridades_consolidadas = []
        seen_mods = set()
        for modulo in SYSTEM_MODULES:
            p = permisos_by_mod[modulo]
            seguridades_consolidadas.append({
                "id_seguridad": p.get("id_seguridad", 0),
                "id_usuario": self.id_usuario,
                "modulo": modulo,
                "ver": bool(p["ver"]),
                "crear": bool(p["crear"]),
                "editar": bool(p["editar"]),
                "eliminar": bool(p["eliminar"]),
            })
            seen_mods.add(modulo)

        for s in seguridades_response:
            mod_upper = (s.get("modulo") or "").strip().upper()
            if mod_upper and mod_upper not in seen_mods:
                seguridades_consolidadas.append(s)
                seen_mods.add(mod_upper)

        return {
            "id_usuario": self.id_usuario,
            "rut": self.rut or "",
            "nombre": self.nombre,
            "login": self.login,
            "correo": self.correo,
            "telefono": self.telefono or "",
            "url_firma": self.url_firma,
            "rol": rol_value,
            "activo": bool(self.activo),
            "seguridades": seguridades_consolidadas,
            "permissions": permisos_by_mod,
            "permisos": permisos_by_mod,
        }
