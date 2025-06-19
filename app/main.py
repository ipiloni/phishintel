import os
from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.db_config import Base, engine
from app.controllers.usuariosController import UsuariosController

# Flask es la libreria que vamos a usar para generar los Endpoints
app = Flask(__name__)

Base.metadata.create_all(engine)

########## ENDPOINTS ##########
@app.route("/usuarios", methods=["POST"])
def crearUsuario():
    data = request.get_json()
    return UsuariosController.crearUsuario(data)

if __name__ == "__main__":
    app.run(debug=True, port=8080)