from app.db.base import Base
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship, backref

class Gasto(Base):
    __tablename__ = "gasto"

    id_gasto  = Column(Integer, primary_key=True, autoincrement=True)
    nombre    = Column(String(100), nullable=False)
    es_gasto  = Column(Boolean, nullable=False)
    es_costo  = Column(Boolean, nullable=False)

  
    def __repr__(self):
        return f"<Gasto {self.id_gasto} {self.nombre}>"
