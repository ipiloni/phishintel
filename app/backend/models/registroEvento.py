from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config.db_config import Base

class RegistroEvento(Base):
    __tablename__ = "registrosEventos"

    idRegistroEvento = Column(Integer, primary_key=True, autoincrement=True)
    idEvento = Column(Integer, ForeignKey("eventos.idEvento"), unique=True)
    # Emails
    asunto = Column(String(255), nullable=True)
    cuerpo = Column(String(10000), nullable=True)
    # SMS o Whatsapp
    mensaje = Column(String(5000), nullable=True)

    # Para llamadas utilizaremos el prompt inicial u objetivo en la columna 'mensaje' y la conversacion estará en 'cuerpo'

    evento = relationship("Evento", back_populates="registroEvento")