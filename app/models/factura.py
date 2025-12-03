# src/models/factura.py
from datetime import datetime, date
from sqlalchemy import Integer, String, Date, ForeignKey, Column
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy import event

def _to_date(v):
    """Acepta date o string ('YYYY-MM-DD', 'DD-MM-YYYY', 'YYYYMMDD', 'DDMMYYYY')."""
    if v is None or isinstance(v, date):
        return v
    s = str(v).strip().replace("/", "-")
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y%m%d", "%d%m%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None

class Factura(Base):
    __tablename__ = "factura"

    id_factura = Column(Integer, primary_key=True, autoincrement=True, index=True)

    fecha_creacion = Column(Date, nullable=False)
    fecha_emision = Column(Date, nullable=False)
    folio_sii = Column(Integer, nullable=False)
    terms = Column(String(200), nullable=False)

    carta_credito = Column(String(50))
    fecha_carta_credito = Column(String(50))

    id_ide = Column(Integer, ForeignKey("ide.id_ide"), nullable=False)

    subtotal = Column(String(13))
    total = Column(String(13))
    descuento = Column(String(13))
    contract = Column(String(200))
    nota = Column(String(3000))
    nota_al_pie = Column(String(1000))

    Ide = relationship("Ide", back_populates="Facturas", foreign_keys=[id_ide])

    DetalleFactura = relationship(
        "DetalleFactura",
        back_populates="Factura",
        lazy="dynamic",
        foreign_keys="DetalleFactura.id_factura",
    )

    def __repr__(self):
        return f"<Factura {self.id_factura} folio={self.folio_sii} ide={self.id_ide}>"

    def to_dict(self):
        return {
            "id_factura": self.id_factura,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_emision": self.fecha_emision.isoformat() if self.fecha_emision else None,
            "folio_sii": self.folio_sii,
            "terms": self.terms,
            "carta_credito": self.carta_credito,
            "fecha_carta_credito": self.fecha_carta_credito,
            "id_ide": self.id_ide,
            "subtotal": self.subtotal,
            "total": self.total,
            "descuento": self.descuento,
            "contract": self.contract,
            "nota": self.nota,
            "nota_al_pie": self.nota_al_pie,
        }




@event.listens_for(Factura, "before_insert")
@event.listens_for(Factura, "before_update")
def _normalize_dates(mapper, connection, target: Factura):
    target.fecha_creacion = _to_date(target.fecha_creacion)
    target.fecha_emision  = _to_date(target.fecha_emision)
