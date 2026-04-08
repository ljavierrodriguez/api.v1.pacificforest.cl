from sqlalchemy import Column, Integer, String, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.seguridad import Seguridad

# Import security helpers lazily inside methods to avoid circular imports

OPEN_ACCESS_MODULES = (
    "AGENTE",
    "BODEGA",
    "CIUDAD",
    "CLASE",
    "CLAUSULA_VENTA",
    "CLIENTE_PROV",
    "CLIENTE_PROVEEDOR",
    "CONTACTO",
    "CONTACTO_ODC",
    "CONTACTO_ORDEN_COMPRA",
    "CONTACTO_PROF",
    "CONTACTO_PROFORMA",
    "CONTENEDOR",
    "DETALLE_FACTURA",
    "DETALLE_GASTO",
    "DETALLE_IDE",
    "DETALLE_ORDEN_COMPRA",
    "DETALLE_PL",
    "DETALLE_PROFORMA",
    "DIRECCION",
    "DOCUMENTO_IDE",
    "EMPRESA",
    "ESPECIE",
    "ESTADO_DET_PLE",
    "ESTADO_ODC",
    "ESTADO_OE",
    "ESTADO_PL",
    "ESTADO_PROFORMA",
    "EXPORTACION",
    "FACTURA",
    "FORMA_PAGO",
    "GASTO",
    "IDE",
    "INFORME",
    "INFORMES",
    "INVENTARIO",
    "MANTENEDORES",
    "MONEDA",
    "NAVIERA",
    "OPER_EXPORT",
    "OPERACION_EXPORTACION",
    "ORDENCOMPRA",
    "ORDEN_COMPRA",
    "PAIS",
    "PARAMETRO",
    "PLC",
    "PLE",
    "PRODUCTO",
    "PROFITANDLOSS",
    "PROFORMA",
    "PUERTO",
    "SEGURIDAD",
    "TIPO_COMISION",
    "TIPO_ENVASE",
    "UNIDAD_MEDIDA",
    "UNIDAD_VENTA",
    "USUARIO",
)


class User(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True, index=True)
    rut = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(120), nullable=False)
    login = Column(String(80), unique=True, index=True, nullable=False)
    pass_ = Column("pass", String(255), nullable=False)
    correo = Column(String(200), unique=True, index=True, nullable=False)
    telefono = Column(String(50), nullable=False)
    url_firma = Column(String(255), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)

    __table_args__ = (UniqueConstraint("login", name="uq_usuario_login"),)

    seguridades = relationship("Seguridad", back_populates="usuario",  lazy="selectin",  cascade="all, delete-orphan")

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

    def __repr__(self):
        return f"<User id={self.id_usuario} login={self.login} activo={self.activo}>"



    """
    def to_dict(self) -> dict:
        perms_by_mod = {
            s.modulo: {
                "crear": bool(s.crear),
                "ver": bool(s.ver),
                "editar": bool(s.editar),
                "eliminar": bool(s.eliminar),
                "id_seguridad": s.id_seguridad,
            }
            for s in (self.seguridades or [])
        }

        return {
            "id_usuario": self.id_usuario,
            "rut": self.rut,
            "nombre": self.nombre,
            "login": self.login,
            "correo": self.correo,
            "telefono": self.telefono,
            "url_firma": self.url_firma,
            "activo": self.activo,
            "permisos": perms_by_mod,
        }

    """
    def to_dict(self) -> dict:
        permissions_by_mod = {}
        permisos_by_mod = {}
        seguridades = self.seguridades or []
        seguridades_response = []

        for s in seguridades:
            modulo = (s.modulo or "").strip().upper()
            if not modulo:
                continue

            id_seguridad = getattr(s, "id_seguridad", 0) or 0

            permissions_by_mod[modulo] = {
                "id_seguridad": id_seguridad,
                "create": True,
                "read": True,
                "update": True,
                "delete": True,
            }

            permisos_by_mod[modulo] = {
                "id_seguridad": id_seguridad,
                "crear": True,
                "ver": True,
                "editar": True,
                "eliminar": True,
            }

            seguridad_data = s.to_dict()
            seguridad_data["crear"] = True
            seguridad_data["ver"] = True
            seguridad_data["editar"] = True
            seguridad_data["eliminar"] = True
            seguridades_response.append(seguridad_data)

        for modulo in OPEN_ACCESS_MODULES:
            permissions_by_mod[modulo] = {
                "id_seguridad": permissions_by_mod.get(modulo, {}).get("id_seguridad", 0),
                "create": True,
                "read": True,
                "update": True,
                "delete": True,
            }
            permisos_by_mod[modulo] = {
                "id_seguridad": permisos_by_mod.get(modulo, {}).get("id_seguridad", 0),
                "crear": True,
                "ver": True,
                "editar": True,
                "eliminar": True,
            }

        return {
            "id_usuario": self.id_usuario,
            "rut": self.rut,
            "nombre": self.nombre,
            "login": self.login,
            "correo": self.correo,
            "telefono": self.telefono,
            "url_firma": self.url_firma,
            "activo": bool(self.activo),

            # legacy (lista)
            "seguridades": seguridades_response,

            # compatibilidad (mapa)
            "permisos": permisos_by_mod,

            # nuevo (mapa)
            "permissions": permissions_by_mod,
        }
