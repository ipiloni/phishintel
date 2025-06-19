import os
from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.controllers.usuariosController import UsuariosController

# Flask es la libreria que vamos a usar para generar los Endpoints
app = Flask(__name__)

# Generamos la base de datos
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "phishintel.db")
engine = create_engine(f"sqlite:///{db_path}")
SessionLocal = sessionmaker(bind=engine)

########## ENDPOINTS ##########
@app.route("/usuarios", methods=["POST"])
def crearUsuario():
    data = request.get_json()
    return UsuariosController.crearUsuario(data)

if __name__ == "__main__":
    app.run(debug=True, port=8080)