from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.config.db_config import Base
from datetime import datetime

class IntentoReporte(Base):
    __tablename__ = 'intentos_reporte'

    idIntentoReporte = Column(Integer, primary_key=True, autoincrement=True)
    idUsuario = Column(Integer, ForeignKey('usuarios.idUsuario'), nullable=False)
    tipoEvento = Column(String, nullable=False)
    fechaInicio = Column(DateTime, nullable=False)
    fechaFin = Column(DateTime, nullable=False)
    fechaIntento = Column(DateTime, default=datetime.utcnow, nullable=False)
    verificado = Column(Boolean, default=False, nullable=False)
    resultadoVerificacion = Column(Text, nullable=True)  # Para guardar detalles del resultado
    idEventoVerificado = Column(Integer, ForeignKey('eventos.idEvento'), nullable=True)  # Si se encontró el evento

    # Relaciones
    usuario = relationship("Usuario", back_populates="intentosReporte")
    eventoVerificado = relationship("Evento", back_populates="intentosReporte")

    def get(self):
        return {
            "idIntentoReporte": self.idIntentoReporte,
            "idUsuario": self.idUsuario,
            "tipoEvento": self.tipoEvento,
            "fechaInicio": self.fechaInicio.isoformat() if self.fechaInicio else None,
            "fechaFin": self.fechaFin.isoformat() if self.fechaFin else None,
            "fechaIntento": self.fechaIntento.isoformat() if self.fechaIntento else None,
            "verificado": self.verificado,
            "resultadoVerificacion": self.resultadoVerificacion,
            "idEventoVerificado": self.idEventoVerificado
        }
