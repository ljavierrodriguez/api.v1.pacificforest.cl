from sqlalchemy import Integer, String, Boolean, Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from app.db.base import Base


class DocumentoIde(Base):
    __tablename__ = "documento_ide"

    id_documento_ide = Column(Integer, primary_key=True, autoincrement=True)
    id_ide = Column(Integer, ForeignKey("ide.id_ide"), nullable=True)

    descripcion = Column(String(100), nullable=False)
    nombre_original = Column(String(200), nullable=True)
    nombre_archivo = Column(String(200), nullable=True)
    enviado = Column(Boolean, nullable=True, default=False)

    def __repr__(self):
        return f"<DocumentoIde {self.id_documento_ide} ide={self.id_ide} enviado={self.enviado}>"
