from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
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
    idArea = Column(Integer, ForeignKey('areas.idArea'), nullable=True)
    idVoz = Column(String, nullable=True) #Si este es null, entonces sacamos el boton de crear voz  (Sale el modal este) Sino ya esta creada
    perfilLinkedin = Column(String, nullable=True)

    area = relationship("Area", back_populates="usuarios")

    # Relación con eventos a través de UsuarioxEvento
    eventosAsociados = relationship("UsuarioxEvento", back_populates="usuario")
    
    # Relación con intentos de reporte
    intentosReporte = relationship("IntentoReporte", back_populates="usuario")

    def get(self):
        return {
            "idUsuario": self.idUsuario,
            "nombreUsuario": self.nombreUsuario,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "correo": self.correo,
            "telefono": self.telefono,
            "esAdministrador": self.esAdministrador,
            "idArea": self.idArea,
            "idVoz": self.idVoz,
            "perfilLinkedin": self.perfilLinkedin
        }
