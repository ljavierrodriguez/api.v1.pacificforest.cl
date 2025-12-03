from sqlalchemy import Integer, String, Column
from app.db.base import Base


class Parametro(Base):
    __tablename__ = "parametro"

    id_parametro = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nota_1 = Column(String(1000), nullable=False)

    def to_dict(self):
        return {"id_parametro": self.id_parametro, "nota_1": self.nota_1}

    def __repr__(self):
        return f"<Parametro {self.id_parametro}>"
