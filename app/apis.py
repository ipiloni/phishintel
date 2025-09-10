from flask import request, Blueprint, send_file

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
from flask_cors import CORS
import os

# Flask es la libreria que vamos a usar para generar los Endpoints
apis = Blueprint("apis", __name__)

CORS(apis, resources={r"/api/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True)
# =================== ENDPOINTS =================== #
# ------ # LLAMADAS TWILIO # ------ #
@apis.route("/api/audios/<nombreAudio>", methods=["GET"])
def enviarAudio(nombreAudio):
    return exponerAudio(nombreAudio)

def exponerAudio(nombreAudio): # es una funcion que nos permite reutilizarla internamente
    return send_file(f"./audios/{nombreAudio}", mimetype="audio/mpeg")

@apis.route("/api/twilio/respuesta", methods=["POST"])
def procesarRespuestaLlamadaTwilio():
    speech = request.form.get("SpeechResult")
    confidence = request.form.get("Confidence")
    return LlamadasController.procesarRespuesta(speech, confidence)

@apis.route("/api/llamadas", methods=["POST"])
def generarLlamada():
    data = request.get_json()
    return LlamadasController.llamar(data)

# ------ # TRANSFORMADORES TTS Y STT # ------ #
@apis.route("/api/tts", methods=["POST"])
def generarTTS():
    data = request.get_json()
    return ElevenLabsController().generarTTS(data)

@apis.route("/api/stt", methods=["POST"])
def generarSTT():
    data = request.get_json()
    ubicacion = data["ubicacion"]
    return ElevenLabsController().generarSTT(ubicacion)

# ------ # MENSAJES # ------ #
@apis.route("/api/mensajes/whatsapp", methods=["POST"])
def enviarMensajeWhatsapp():
    data = request.get_json()
    return MensajesController.enviarMensajeWhatsapp(data)

@apis.route("/api/mensajes/sms", methods=["POST"])
def enviarMensajeSMS():
    data = request.get_json()
    return MensajesController.enviarMensajeSMS(data)

# ------ # REGISTROS DE EVENTOS +  # ------ #
@apis.route("/api/sumar-falla", methods=["GET"])
def sumarFalla():
    idUsuario = request.args.get("idUsuario", type=int)
    idEvento = request.args.get("idEvento", type=int)
    if not idUsuario or not idEvento:
        return responseError("CAMPOS_OBLIGATORIOS", "Faltan parámetros 'idUsuario' o 'idEvento'", 400)
    log.info(f"se sumará una falla al usuario '{str(idUsuario)}' del evento '{str(idEvento)}'")
    return FallaController.sumarFalla(idUsuario, idEvento)

@apis.route("/api/eventos", methods=["GET"])
def obtenerEventos():
    return EventosController.obtenerEventos()

@apis.route("/api/eventos/<int:idEvento>", methods=["GET"])
def obtenerEventoPorId(idEvento):
    return EventosController.obtenerEventoPorId(idEvento)

@apis.route("/api/eventos", methods=["POST"])
def crearEvento():
    data = request.get_json()
    return EventosController.crearEvento(data)

@apis.route("/api/eventos/<int:idEvento>", methods=["PUT"])
def editarEvento(idEvento):
    data = request.get_json()
    return EventosController.editarEvento(idEvento, data)

@apis.route("/api/eventos/<int:idEvento>/usuarios/<int:idUsuario>", methods=["POST"])
def asociarUsuarioEvento(idEvento, idUsuario):
    data = request.get_json()
    resultado_val = data.get("resultado")
    if not resultado_val:
        return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo 'resultado'", 400)
    return EventosController.asociarUsuarioEvento(idEvento, idUsuario, resultado_val)

@apis.route("/api/eventos/<int:idEvento>", methods=["DELETE"])
def eliminarEvento(idEvento):
    return EventosController.eliminarEvento(idEvento)

# ------ # ENVIO DE EMAILS # ------ #
@apis.route("/api/email/notificar", methods=["POST"]) # Esta ruta envia una notificacion con el email de PhishIntel
def notificarViaEmail():
    data = request.get_json()
    return EmailController.enviarNotificacionPhishintel(data)

@apis.route("/api/email/enviar", methods=["POST"]) # Esta ruta
def enviarEmail():
    data = request.get_json()
    return EmailController.enviarMail(data)

@apis.route("/api/email/enviar-id", methods=["POST"]) # Esta ruta
def enviarEmailPorID():
    data = request.get_json()
    return EmailController.enviarMailPorID(data)

@apis.route("/api/email/generar", methods=["POST"]) # Esta ruta llama a gemini y genera un asunto y texto en html
def llamarIAGemini():
    data = request.get_json()
    return AIController.armarEmail(data)

@apis.route("/api/email/generar-enviar", methods=["POST"])
def generarYEnviarEmail():
    data = request.get_json()
    return EmailController.generarYEnviarMail(data)

# =================== ABM =================== #

# ------ # USUARIOS # ------ #
@apis.route("/api/usuarios", methods=["GET"])
def obtenerUsuarios():
    return UsuariosController.obtenerTodosLosUsuarios()

@apis.route("/api/usuarios/<idUsuario>", methods=["GET"])
def obtenerUsuario(idUsuario):
    return UsuariosController.obtenerUsuario(idUsuario)

@apis.route("/api/usuarios", methods=["POST"])
def crearUsuario():
    data = request.get_json()
    return UsuariosController.crearUsuario(data)

@apis.route("/api/usuarios/<idUsuario>", methods=["DELETE"])
def eliminarUsuario(idUsuario):
    return UsuariosController.eliminarUsuario(idUsuario)

@apis.route("/api/usuarios/<idUsuario>", methods=["PUT"])
def editarUsuario(idUsuario):
    data = request.get_json()
    return UsuariosController.editarUsuario(idUsuario, data)

# ------ # AREAS # ------ #
@apis.route("/api/areas", methods=["GET"])
def obtenerAreas():
    return AreasController.obtenerTodasLasAreas()

@apis.route("/api/areas", methods=["POST"])
def crearArea():
    data = request.get_json()
    return AreasController.crearArea(data)

@apis.route("/api/areas/<idArea>", methods=["GET"])
def obtenerArea(idArea):
    return AreasController.obtenerArea(idArea)

@apis.route("/api/areas/<idArea>", methods=["DELETE"])
def eliminarArea(idArea):
   return AreasController.eliminarArea(idArea)

@apis.route("/api/areas/<idArea>", methods=["PUT"])
def editarArea(idArea):
    data = request.get_json()
    return AreasController.editarArea(idArea, data)