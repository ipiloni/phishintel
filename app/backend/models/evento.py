from sqlalchemy import Column, Integer, DateTime, Enum as SQLEnum, String
from sqlalchemy.orm import relationship
from app.config.db_config import Base

from app.backend.models.tipoEvento import TipoEvento

class Evento(Base):
    __tablename__ = 'eventos'

    idEvento = Column(Integer, primary_key=True, autoincrement=True)
    tipoEvento = Column(SQLEnum(TipoEvento), nullable=False)
    fechaEvento = Column(DateTime, nullable=False)
    dificultad = Column(String(20), nullable=True)  # 'Fácil', 'Medio', 'Difícil' - solo para MENSAJE y CORREO
    medio = Column(String(20), nullable=True)  # 'whatsapp', 'telegram', 'sms' - solo para MENSAJE

    # Relación con Registro (uno a uno)
    registroEvento = relationship("RegistroEvento", uselist=False, back_populates="evento")

    # Relación con usuarios a través de UsuarioxEvento
    usuariosAsociados = relationship("UsuarioxEvento", back_populates="evento")
    
    # Relación con intentos de reporte
    intentosReporte = relationship("IntentoReporte", back_populates="eventoVerificado")