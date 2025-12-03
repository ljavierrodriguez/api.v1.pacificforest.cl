from datetime import datetime, date
from sqlalchemy import Integer, String, Date, Boolean, ForeignKey, event, Column
from app.db.base import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import event

def _to_date(v):
    """Convierte 'YYYY-MM-DD', 'DD-MM-YYYY', 'YYYYMMDD', 'DDMMYYYY' a date; deja None si no matchea."""
    if v is None or isinstance(v, date):
        return v
    s = str(v).strip().replace("/", "-")
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y%m%d", "%d%m%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None

class Plc(Base):
    __tablename__ = "plc"

    # === columnas (equivalentes a Yii) ===
    id_plc                   = Column(Integer, primary_key=True, autoincrement=True)
    id_operacion_exportacion = Column(Integer, ForeignKey("operacion_exportacion.id_operacion_exportacion"), nullable=True)
    id_estado_pl             = Column(Integer, ForeignKey("estado_pl.id_estado_pl"), nullable=False)

    # En Yii es string + beforeSave -> date. Aquí lo guardamos como Date.
    fecha_creacion           = Column(Date, nullable=False)

    volumen_m3               = Column(String(12), nullable=True)
    paquetes                 = Column(Integer, nullable=False)
    peso_bruto               = Column(String(12), nullable=False)
    piezas                   = Column(Integer, nullable=False)
    rw                       = Column(Boolean, nullable=True)
    rl                       = Column(Boolean, nullable=True)
    descripcion              = Column(String(200), nullable=False)
    categoria_fsc            = Column(String(20), nullable=True)

    # === relaciones ===
    # BELONGS_TO EstadoPl y OperacionExportacion   
    EstadoPl = relationship(
        "EstadoPl",
        backref=backref("Plcs", lazy="dynamic"),
        foreign_keys=[id_estado_pl],
    )
    OperacionExportacion = relationship(
        "OperacionExportacion",
        backref=backref("Plcs", lazy="dynamic"),
        foreign_keys=[id_operacion_exportacion],
    )

    # HAS_MANY DetallePl.id_plc y DetalleIde.id_plc
    # (usa backref para crear DetallePl.Plc y DetalleIde.Plc automáticamente)
    DetallePl = relationship(
        "DetallePl",
        backref=backref("Plc"),
        lazy="dynamic",
        foreign_keys="DetallePl.id_plc",
        # cascade="all, delete-orphan",  # opcional si quieres borrar hijos al borrar el PLC
        # single_parent=True,            # usar junto con delete-orphan
    )
   
    def __repr__(self):
        return f"<Plc {self.id_plc} oe={self.id_operacion_exportacion} estado={self.id_estado_pl}>"

# === Hook estilo beforeSave de Yii para normalizar la fecha ===
@event.listens_for(Plc, "before_insert")
@event.listens_for(Plc, "before_update")
def _normalize_fecha_creacion(mapper, connection, target: Plc):
    target.fecha_creacion = _to_date(target.fecha_creacion)
