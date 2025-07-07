from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import relationship
from app.config.db_config import Base

class Usuario(Base):
    __tablename__ = 'usuarios'

    idUsuario = Column(Integer, primary_key=True, autoincrement=True)
    nombreUsuario = Column(String, nullable=False)
    password = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    direccion = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    correo = Column(String, nullable=True)
    esAdministrador = Column(Boolean, nullable=True)

    eventos = relationship("Evento", secondary="Usuario_Evento", back_populates="usuarios")