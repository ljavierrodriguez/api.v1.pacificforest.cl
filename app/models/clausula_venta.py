from sqlalchemy import String, Column
from sqlalchemy.orm import relationship
from app.db.base import Base


class ClausulaVenta(Base):
    __tablename__ = "clausula_venta"

    id_clausula_venta = Column(String(10), primary_key=True, nullable=False)

    Proformas = relationship(
        "Proforma",
        back_populates="ClausulaVenta",
        lazy="dynamic",
        cascade=None,
        passive_deletes=False,
    )

    def __repr__(self):
        return f"<ClausulaVenta {self.id_clausula_venta}>"
