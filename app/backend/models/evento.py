from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from app.backend.models.resultadoEvento import ResultadoEvento
from app.backend.models.tipoEvento import TipoEvento
from app.config.base import Usuario_Evento
from app.config.db_config import Base

from sqlalchemy import Enum as SQLEnum


class Evento(Base):
    __tablename__ = 'eventos'

    idEvento = Column(Integer, primary_key=True)
    tipoEvento = Column(SQLEnum(TipoEvento), nullable=False)
    usuarios = relationship("Usuario", secondary=Usuario_Evento, back_populates="eventos")
    fechaEvento = Column(DateTime, nullable=False)
    resultado = Column(SQLEnum(ResultadoEvento), nullable=False)
    registro = relationship("Registro", uselist=False, back_populates="eventos")
