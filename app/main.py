from flask import Flask, request, jsonify

from app.config.db_config import Base, engine
from app.controllers.aiController import AIController
from app.controllers.emailController import EmailController
from app.controllers.usuariosController import UsuariosController

# Flask es la libreria que vamos a usar para generar los Endpoints
app = Flask(__name__)

Base.metadata.create_all(engine)

########## ENDPOINTS ##########
# ------ # REGISTRO DE EVENTOS # ------ #
@app.route("/registro", methods=["GET"])
def registrarClic():
    print(f"Mira el tipo como apreto el boton no te puedo creer!")
    return jsonify({"mensaje": "Como caiste pichon"})

# ------ # ENVIO DE EMAILS # ------ #
@app.route("/email", methods=["POST"])
def enviarEmail():
    data = request.get_json()
    return EmailController.enviarMail(data)

# ------ # GEMINI AI # ------ #
@app.route("/email/gemini", methods=["POST"])
def llamarIAGemini():
    data = request.get_json()
    return AIController.armarEmailGemini(data)

# ------ # USUARIOS # ------ #
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

@app.route("/usuarios/<idUsuario>", methods=["PUT"])
def editarUsuario(idUsuario):
    data = request.get_json()
    return UsuariosController.editarUsuario(idUsuario, data)

if __name__ == "__main__":
    app.run(debug=True, port=8080)