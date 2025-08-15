from flask import Flask, request, send_from_directory

from app.backend.models.error import responseError
from app.config.db_config import Base, engine
from app.controllers.abm.areasController import AreasController
from app.controllers.emails.aiController import AIController
from app.controllers.llamadas.elevenLabsController import ElevenLabsController
from app.controllers.emails.emailController import EmailController
from app.controllers.abm.eventosController import EventosController
from app.controllers.llamadas.llamadasController import LlamadasController
from app.controllers.abm.usuariosController import UsuariosController
from app.controllers.fallaController import FallaController
from app.controllers.mensajes.mensajesController import MensajesController
from app.utils.logger import log
import os

# Flask es la libreria que vamos a usar para generar los Endpoints
app = Flask(__name__)

Base.metadata.create_all(engine)

# =================== ENDPOINTS =================== #

# ------ # TRANSFORMADORES TTS Y STT # ------ #
@app.route("/api/tts", methods=["POST"])
def generarTTS():
    data = request.get_json()
    return ElevenLabsController().generarTTS(data)

@app.route("/api/stt", methods=["POST"])
def generarSTT():
    data = request.get_json()
    ubicacion = data["ubicacion"]
    return ElevenLabsController().generarSTT(ubicacion)

# ------ # MENSAJES # ------ #
@app.route("/api/mensajes/whatsapp", methods=["POST"])
def enviarMensajeWhatsapp():
    data = request.get_json()
    return MensajesController.enviarMensajeWhatsapp(data)

@app.route("/api/mensajes/sms", methods=["POST"])
def enviarMensajeSMS():
    data = request.get_json()
    return MensajesController.enviarMensajeSMS(data)

# ------ # LLAMADA # ------ #
@app.route("/api/llamadas", methods=["POST"])
def generarLlamada():
    data = request.get_json()
    return LlamadasController.llamar(data)

# ------ # REGISTROS DE EVENTOS +  # ------ #
@app.route("/api/sumar-falla", methods=["GET"])
def sumarFalla():
    idUsuario = request.args.get("idUsuario", type=int)
    idEvento = request.args.get("idEvento", type=int)
    if not idUsuario or not idEvento:
        return responseError("CAMPOS_OBLIGATORIOS", "Faltan parámetros 'idUsuario' o 'idEvento'", 400)
    log.info(f"se sumará una falla al usuario '{str(idUsuario)}' del evento '{str(idEvento)}'")
    return FallaController.sumarFalla(idUsuario, idEvento)

@app.route("/api/eventos", methods=["GET"])
def obtenerEventos():
    return EventosController.obtenerEventos()

@app.route("/api/eventos/<int:idEvento>", methods=["GET"])
def obtenerEventoPorId(idEvento):
    return EventosController.obtenerEventoPorId(idEvento)

@app.route("/api/eventos", methods=["POST"])
def crearEvento():
    data = request.get_json()
    return EventosController.crearEvento(data)

@app.route("/api/eventos/<int:idEvento>", methods=["PUT"])
def editarEvento(idEvento):
    data = request.get_json()
    return EventosController.editarEvento(idEvento, data)

@app.route("/api/eventos/<int:idEvento>/usuarios/<int:idUsuario>", methods=["POST"])
def asociarUsuarioEvento(idEvento, idUsuario):
    data = request.get_json()
    resultado_val = data.get("resultado")
    if not resultado_val:
        return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo 'resultado'", 400)
    return EventosController.asociarUsuarioEvento(idEvento, idUsuario, resultado_val)

@app.route("/api/eventos/<int:idEvento>", methods=["DELETE"])
def eliminarEvento(idEvento):
    return EventosController.eliminarEvento(idEvento)

# ------ # ENVIO DE EMAILS # ------ #
@app.route("/api/email/enviar", methods=["POST"]) # Esta ruta
def enviarEmail():
    data = request.get_json()
    return EmailController.enviarMail(data)

@app.route("/api/email/generar", methods=["POST"]) # Esta ruta llama a gemini y genera un asunto y texto en html
def llamarIAGemini():
    data = request.get_json()
    return AIController.armarEmail(data)

@app.route("/api/email/generar-enviar", methods=["POST"])
def generarYEnviarEmail():
    data = request.get_json()
    return EmailController.generarYEnviarMail(data)

# =================== ABM =================== #

# ------ # USUARIOS # ------ #
@app.route("/api/usuarios", methods=["GET"])
def obtenerUsuarios():
    return UsuariosController.obtenerTodosLosUsuarios()

@app.route("/api/usuarios/<idUsuario>", methods=["GET"])
def obtenerUsuario(idUsuario):
    return UsuariosController.obtenerUsuario(idUsuario)

@app.route("/api/usuarios", methods=["POST"])
def crearUsuario():
    data = request.get_json()
    return UsuariosController.crearUsuario(data)

@app.route("/api/usuarios/<idUsuario>", methods=["DELETE"])
def eliminarUsuario(idUsuario):
    return UsuariosController.eliminarUsuario(idUsuario)

@app.route("/api/usuarios/<idUsuario>", methods=["PUT"])
def editarUsuario(idUsuario):
    data = request.get_json()
    return UsuariosController.editarUsuario(idUsuario, data)

# ------ # AREAS # ------ #
@app.route("/api/areas", methods=["GET"])
def obtenerAreas():
    return AreasController.obtenerTodasLasAreas()

@app.route("/api/areas", methods=["POST"])
def crearArea():
    data = request.get_json()
    return AreasController.crearArea(data)

@app.route("/api/areas/<idArea>", methods=["GET"])
def obtenerArea(idArea):
    return AreasController.obtenerArea(idArea)

@app.route("/api/areas/<idArea>", methods=["DELETE"])
def eliminarArea(idArea):
   return AreasController.eliminarArea(idArea)

@app.route("/api/areas/<idArea>", methods=["PUT"])
def editarArea(idArea):
    data = request.get_json()
    return AreasController.editarArea(idArea, data)

# ------ # FRONTEND # ------ #
# Ruta para servir el index.html
# Ruta para el index
@app.route("/")
def index():
    return send_from_directory(os.path.join(app.root_path, "frontend"), "index.html")

@app.route("/login")
def login():
   return send_from_directory(os.path.join(app.root_path, "frontend"), "login.html")

@app.route("/registro")
def registro():
   return send_from_directory(os.path.join(app.root_path, "frontend"), "register.html")

@app.route("/reportes")
def reportes():
   return send_from_directory(os.path.join(app.root_path, "frontend"), "reportes.html")

@app.route("/principal")
def principal():
   return send_from_directory(os.path.join(app.root_path, "frontend"), "principal.html")
@app.route("/usuarios")
def usuarios():
   return send_from_directory(os.path.join(app.root_path, "frontend"), "usuarios.html")

# Ruta para cualquier otro archivo dentro de frontend (CSS, JS, imágenes, vendor, etc.)
@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(os.path.join(app.root_path, "frontend"), filename)

# =================== MAIN =================== #
if __name__ == "__main__":
    app.run(debug=True, port=8080)
# =================== MAIN =================== #