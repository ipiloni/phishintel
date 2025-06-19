import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Ruta absoluta al archivo de base de datos
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "../../phishintel.db")

# Conexión a la base
engine = create_engine(f"sqlite:///{db_path}")

# Session
SessionLocal = sessionmaker(bind=engine)

# Base declarativa
Base = declarative_base()