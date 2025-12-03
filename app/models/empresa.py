from __future__ import annotations
from sqlalchemy import event, update, UniqueConstraint, Integer, String, Boolean, ForeignKey, Column
from app.db.base import Base

def rut_unformat(rut: str) -> str:
    if not rut: return ""
    return rut.replace(".", "").replace("-", "").upper().strip()

def rut_format(rut: str) -> str:
    r = rut_unformat(rut)
    if len(r) < 2: return r
    cuerpo, dv = r[:-1], r[-1]
    parts = []
    while cuerpo:
        parts.append(cuerpo[-3:])
        cuerpo = cuerpo[:-3]
    return ".".join(reversed(parts)) + "-" + dv

class Empresa(Base):
    __tablename__ = "empresa"

    id_empresa = Column(Integer, primary_key=True)
    rut = Column(String(15), nullable=False)
    nombre_fantasia = Column(String(200), nullable=False)
    razon_social = Column(String(200), nullable=False)
    direccion = Column(String(200), nullable=False)
    telefono_1 = Column(String(50))
    telefono_2 = Column(String(50))
    giro = Column(String(200))
    id_ciudad = Column(Integer, ForeignKey("ciudad.id_ciudad"), nullable=False)
    es_vigente = Column(Boolean, default=True, nullable=False)
    en_proforma = Column(Boolean, default=False, nullable=False)
    en_odc = Column(Boolean, default=False, nullable=False)
    por_defecto = Column(Boolean, default=False, nullable=False)
    url_logo = Column(String(100), nullable=False)

    __table_args__ = (
        # si tu BD lo permite, es buena idea que el RUT sea único
        UniqueConstraint("rut", name="uq_empresa_rut"),
    )

    def serialize(self) -> dict:
        return {
            "id_empresa": self.id_empresa,
            "rut": rut_format(self.rut) if self.rut else None,
            "nombre_fantasia": self.nombre_fantasia,
            "razon_social": self.razon_social,
            "direccion": self.direccion,
            "telefono_1": self.telefono_1,
            "telefono_2": self.telefono_2,
            "giro": self.giro,
            "id_ciudad": self.id_ciudad,
            "es_vigente": self.es_vigente,
            "en_proforma": self.en_proforma,
            "en_odc": self.en_odc,
            "por_defecto": self.por_defecto,
            "url_logo": self.url_logo,
        }

    def __repr__(self):
        return f"<Empresa id={self.id_empresa} rut={self.rut} nombre={self.nombre_fantasia!r}>"

# --- Eventos para emular Yii::beforeSave ---
@event.listens_for(Empresa, "before_insert")
def _empresa_before_insert(mapper, connection, target: Empresa):
    # Normaliza el RUT antes de insertar
    target.rut = rut_format(target.rut)

@event.listens_for(Empresa, "before_update")
def _empresa_before_update(mapper, connection, target: Empresa):
    # Normaliza el RUT si cambió
    if target.rut:
        target.rut = rut_format(target.rut)

@event.listens_for(Empresa, "after_insert")
def _empresa_after_insert(mapper, connection, target: Empresa):
    # Si se marcó como por_defecto, desmarca las demás
    if target.por_defecto:
        stmt = (
            update(Empresa.__table__)
            .where(Empresa.id_empresa != target.id_empresa)
            .where(Empresa.por_defecto == True)
            .values(por_defecto=False)
        )
        connection.execute(stmt)

@event.listens_for(Empresa, "after_update")
def _empresa_after_update(mapper, connection, target: Empresa):
    # Si se cambió a por_defecto=True, desmarca las demás
    if target.por_defecto:
        stmt = (
            update(Empresa.__table__)
            .where(Empresa.id_empresa != target.id_empresa)
            .where(Empresa.por_defecto == True)
            .values(por_defecto=False)
        )
        connection.execute(stmt)
