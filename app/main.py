from config.db_config import Base, engine, SessionLocal
from backend.models import Usuario

Base.metadata.create_all(bind=engine) # Crea todas las tablas

# Crear sesión y testear insert
session = SessionLocal()
nuevo_usuario = Usuario(nombre="Ignacio", correo="ignacio@phishintel.com")
session.add(nuevo_usuario)
session.commit()
session.close()