import enum

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.config.base import Base


class Registro(Base):
    __tablename__ = "registros"

    idRegistro = Column(Integer, primary_key=True, autoincrement=True)
    idEvento = Column(Integer, ForeignKey("eventos.idEvento"), unique=True)

    evento = relationship("Evento", back_populates="registros")
