from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from app.config.db_config import Base
from app.backend.models.resultadoEvento import ResultadoEvento

class UsuarioxEvento(Base):
    __tablename__ = 'usuariosxeventos'

    idUsuario = Column(Integer, ForeignKey('usuarios.idUsuario'), primary_key=True)
    idEvento = Column(Integer, ForeignKey('eventos.idEvento'), primary_key=True)

    resultado = Column(SQLEnum(ResultadoEvento), nullable=False)
    fechaReporte = Column(DateTime, nullable=True)
    fechaFalla = Column(DateTime, nullable=True)

    # Relaciones hacia Usuario y Evento
    usuario = relationship("Usuario", back_populates="eventosAsociados")
    evento = relationship("Evento", back_populates="usuariosAsociados")
