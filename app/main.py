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
@app.route("/usuarios", methods=["GET"])
def obtenerUsuarios():
    return UsuariosController.obtenerUsuarios()

@app.route("/usuarios/<idUsuario>", methods=["GET"])
def obtenerUsuario(idUsuario):
    return UsuariosController.obtenerUsuario(idUsuario)

@app.route("/usuarios", methods=["POST"])
def crearUsuario():
    data = request.get_json()
    return UsuariosController.crearUsuario(data)

@app.route("/usuarios/<idUsuario>", methods=["DELETE"])
def eliminarUsuario(idUsuario):
    return UsuariosController.eliminarUsuario(idUsuario)

if __name__ == "__main__":
    app.run(debug=True, port=8080)