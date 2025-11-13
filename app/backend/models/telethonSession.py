from sqlalchemy import Column, String, Boolean, Integer, DateTime, LargeBinary
from sqlalchemy.sql import func
from app.config.db_config import Base


class TelethonSession(Base):
    __tablename__ = 'telethon_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sessionData = Column(LargeBinary, nullable=True)  # Datos de la sesión serializados (null si está en proceso de auth)
    fechaCreacion = Column(DateTime, nullable=False, server_default=func.now())
    fechaActualizacion = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    estaActiva = Column(Boolean, nullable=False, default=True)
    # Campos para estado de autenticación en proceso
    phone = Column(String, nullable=True)  # Teléfono en proceso de autenticación
    phoneCodeHash = Column(String, nullable=True)  # Hash del código de verificación
    tempSessionString = Column(LargeBinary, nullable=True)  # Sesión temporal durante autenticación

    def get(self):
        return {
            "id": self.id,
            "fechaCreacion": self.fechaCreacion.isoformat() if self.fechaCreacion else None,
            "fechaActualizacion": self.fechaActualizacion.isoformat() if self.fechaActualizacion else None,
            "estaActiva": self.estaActiva
        }

