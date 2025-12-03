from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import relationship
from app.db.base import Base

class EstadoProforma(Base):
    __tablename__ = "estado_proforma"

    id_estado_proforma = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(20), nullable=False) 

   
    Proformas = relationship(
        "Proforma",
        back_populates="EstadoProforma",
        lazy="dynamic"  
    )

    def __repr__(self):
        return f"<EstadoProforma {self.id_estado_proforma} - {self.nombre}>"
    id_estado_proforma = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(20), nullable=False)

    Proformas = relationship(
        "Proforma",
        back_populates="EstadoProforma",
        lazy="dynamic"
    )

    def __repr__(self):
        return f"<EstadoProforma {self.id_estado_proforma} - {self.nombre}>"
