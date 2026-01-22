from sqlalchemy import Column, Integer, String, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.seguridad import Seguridad

# Import security helpers lazily inside methods to avoid circular imports


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
    activo = Column(Boolean, default=True, nullable=False)

    __table_args__ = (UniqueConstraint("login", name="uq_usuario_login"),)

    seguridades = relationship("Seguridad", back_populates="usuario",  lazy="selectin",  cascade="all, delete-orphan")

    # Convenience property expected by some auth code
    @property
    def hashed_password(self) -> str:
        return self.pass_

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
        seguridades = self.seguridades or []

        for s in seguridades:
            modulo = (s.modulo or "").strip().upper()
            if not modulo:
                    continue

            permissions_by_mod[modulo] = {
                "create": bool(s.crear),
                "read": bool(s.ver),
                "update": bool(s.editar),
                "delete": bool(s.eliminar),
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
            "seguridades": [s.to_dict() for s in seguridades],

            # nuevo (mapa)
            "permissions": permissions_by_mod,
            }
