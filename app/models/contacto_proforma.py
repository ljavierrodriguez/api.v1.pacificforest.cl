from sqlalchemy import Integer, ForeignKey, Column
from sqlalchemy.orm import relationship, foreign
from app.db.base import Base


class ContactoProforma(Base):
    __tablename__ = "contacto_proforma"

    id_contacto_proforma = Column(Integer, primary_key=True, autoincrement=True, index=True)

    id_contacto = Column(Integer, ForeignKey("contacto.id_contacto"))
    id_proforma = Column(Integer, ForeignKey("proforma.id_proforma"))

    Contacto = relationship(
        "Contacto",
        primaryjoin="foreign(ContactoProforma.id_contacto)==Contacto.id_contacto",
        back_populates="ContactosProforma",
    )
    Proforma = relationship(
        "Proforma",
        primaryjoin="foreign(ContactoProforma.id_proforma)==Proforma.id_proforma",
        back_populates="ContactosProforma",
    )

    def __repr__(self):
        return f"<ContactoProforma {self.id_contacto_proforma}>"

    def to_dict(self):
        return {
            "id_contacto_proforma": self.id_contacto_proforma,
            "id_contacto": self.id_contacto,
            "id_proforma": self.id_proforma,
        }
