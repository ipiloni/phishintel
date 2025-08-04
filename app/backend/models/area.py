from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from app.config.db_config import Base

class Area(Base):
    __tablename__ = 'areas'

    idArea = Column(Integer, primary_key=True, autoincrement=True)
    nombreArea = Column(String, nullable=False)
    datosDelArea = Column(JSON, nullable=True, default=list)
    usuarios = relationship("Usuario", back_populates="area", cascade="all, delete-orphan")

    def agregarUsuario(self, usuario):
        if usuario not in self.usuarios:
            self.usuarios.append(usuario)
            usuario.area = self

    def quitarUsuario(self, usuario):
        if usuario in self.usuarios:
            self.usuarios.remove(usuario)
            usuario.area = None

    def agregarDato(self, dato: str):
        if self.datosDelArea is None:
            self.datosDelArea = []
        self.datosDelArea.append(dato)

    def quitarDato(self, dato: str):
        if self.datosDelArea and dato in self.datosDelArea:
            self.datosDelArea.remove(dato)

