from sqlalchemy import Column, Integer, String
from app.config.db_config import Base

class Area(Base):
    __tablename__ = 'areas'

    idArea = Column(Integer, primary_key=True, autoincrement=True)
    nombreArea = Column(String, nullable=False)
    # datosDelArea = Column(Lista, nullable=True) que sea una lista de datos importantes del area (se usa para el armado del email, por ej)
    # empleados: los ponemos aca o que cada empleado conozca su area?

