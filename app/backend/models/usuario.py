from sqlalchemy import Column, Integer, String
from app.config.db_config import Base

class Usuario(Base):
    __tablename__ = 'usuarios'

    id_usuario = Column(String, primary_key=True, nullable=False)
    password = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    direccion  = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    correo = Column(String, nullable=False)
