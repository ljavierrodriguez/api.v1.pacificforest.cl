from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, UniqueConstraint, ForeignKey
from app.db.base import Base


class Seguridad(Base):
    __tablename__ = "seguridad"

    id_seguridad = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    modulo = Column(String(15), nullable=False)
    crear = Column(Boolean, nullable=False, default=False)
    ver = Column(Boolean, nullable=False, default=False)
    editar = Column(Boolean, nullable=False, default=False)
    eliminar = Column(Boolean, nullable=False, default=False)

    usuario = relationship("User", back_populates="seguridades")

    __table_args__ = (UniqueConstraint("id_usuario", "modulo", name="uq_seguridad_usuario_modulo"),)

    def __repr__(self):
        return (
            f"<Seguridad u={self.id_usuario} {self.modulo} "
            f"(ver={int(self.ver)}, crear={int(self.crear)}, "
            f"editar={int(self.editar)}, eliminar={int(self.eliminar)})>"
        )

    def to_dict(self) -> dict:
        return {
            "id_seguridad": self.id_seguridad,
            "id_usuario": self.id_usuario,
            "modulo": self.modulo,
            "ver": bool(self.ver),
            "crear": bool(self.crear),
            "editar": bool(self.editar),
            "eliminar": bool(self.eliminar),
        }
