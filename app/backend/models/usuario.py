from sqlalchemy import Column, String, Boolean
from app.config.db_config import Base

class Usuario(Base):
    __tablename__ = 'usuarios'

    idUsuario = Column(String, primary_key=True, nullable=False)
    password = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    direccion  = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    correo = Column(String, nullable=True)
    nombreUsuario = Column(String, nullable=True)
    esAdministrador = Column(Boolean, nullable=True)