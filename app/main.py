from flask import Flask, request, jsonify

from app.config.db_config import Base, engine
from app.controllers.emails.aiController import AIController
from app.controllers.llamadas.elevenLabsController import ElevenLabsController
from app.controllers.emails.emailController import EmailController
from app.controllers.abm.eventosController import EventosController
from app.controllers.llamadas.llamadasController import LlamadasController
from app.controllers.abm.usuariosController import UsuariosController
from app.utils import logger
from app.controllers.fallaController import FallaController
# Flask es la libreria que vamos a usar para generar los Endpoints
app = Flask(__name__)

Base.metadata.create_all(engine)

########## ENDPOINTS ##########
# ------ # TEXT TO SPEECH # ------ #
@app.route("/tts", methods=["POST"])
def generarTTS():
    data = request.get_json()
    texto = data["texto"]
    return ElevenLabsController().generarTTS(texto)

@app.route("/stt", methods=["POST"])
def generarSTT():
    data = request.get_json()
    ubicacion = data["ubicacion"]
    return ElevenLabsController().generarSTT(ubicacion)

# ------ # LLAMADA # ------ #
@app.route("/llamar", methods=["POST"])
def generarLlamada():
    data = request.get_json()
    return LlamadasController.llamar(data)

# ------ # ABM REGISTROS DE EVENTOS +  # ------ #
# Sumar alguna manera de controlar quien produjo la falla
@app.route("/sumarFalla", methods=["GET"])
def sumarFalla():
    return FallaController.sumarFalla()

@app.route("/eventos", methods=["GET"])
def obtenerEventos():
    return EventosController.obtenerEventos()

@app.route("/eventos", methods=["POST"])
def crearEvento():
    data = request.get_json()
    return EventosController.crearEvento(data)

# ------ # ENVIO DE EMAILS # ------ #
@app.route("/email/enviarEmail", methods=["POST"]) # Esta ruta
def enviarEmail():
    data = request.get_json()
    return EmailController.enviarMail(data)

@app.route("/email/generarEmail", methods=["POST"]) # Esta ruta llama a gemini y genera un asunto y texto en html
def llamarIAGemini():
    data = request.get_json()
    return AIController.armarEmailGemini(data)

@app.route("/email/generarYEnviarEmail", methods=["POST"])
def generarYEnviarEmail():
    data = request.get_json()
    return EmailController.generarYEnviarMail(data)

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