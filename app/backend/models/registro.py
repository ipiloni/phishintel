from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config.db_config import Base

class Registro(Base):
    __tablename__ = "registros"

    idRegistro = Column(Integer, primary_key=True, autoincrement=True)
    idEvento = Column(Integer, ForeignKey("eventos.idEvento"), unique=True)
    asunto = Column(String(255), nullable=True)
    cuerpo = Column(String(10000), nullable=True)

    evento = relationship("Evento", back_populates="registro")