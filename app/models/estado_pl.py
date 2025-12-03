from sqlalchemy import Integer, String, Boolean, Column
from sqlalchemy.orm import relationship
from app.db.base import Base


class EstadoPl(Base):
    __tablename__ = "estado_pl"

    id_estado_pl = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(15), nullable=False)
    es_ple = Column(Boolean, default=False)
    es_plc = Column(Boolean, default=False)

    Ples = relationship(
        "Ple",
        back_populates="EstadoPl",
        lazy="dynamic",
        foreign_keys="Ple.id_estado_pl",
    )

    def __repr__(self):
        return f"<EstadoPl {self.id_estado_pl} {self.nombre!r}>"
