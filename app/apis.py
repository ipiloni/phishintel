from flask import request, Blueprint, send_file, jsonify

from app.backend.models.error import responseError
from app.controllers.abm.areasController import AreasController
from app.aiController import AIController
from app.controllers.geminiController import GeminiController
from app.controllers.llamadas.elevenLabsController import ElevenLabsController
from app.controllers.emails.emailController import EmailController
from app.controllers.abm.eventosController import EventosController
from app.controllers.llamadas.llamadasController import LlamadasController
from app.controllers.abm.usuariosController import UsuariosController
from app.controllers.fallaController import FallaController
from app.controllers.mensajes.mensajesController import MensajesController
from app.controllers.mensajes.telegramBot import telegram_bot
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
@apis.route("/api/ia/gemini", methods=["POST"])
def enviarPromptGemini():
    data = request.get_json()
    objetivo = data["objetivo"]
    conversacion = data["conversacion"]
    return GeminiController.generarTexto(objetivo, conversacion)

# ------ # LLAMADAS TWILIO # ------ #
@apis.route("/api/audios/<nombreAudio>", methods=["GET"])
def enviarAudio(nombreAudio):
    return exponerAudio(nombreAudio)

def exponerAudio(nombreAudio): # es una funcion que nos permite reutilizarla internamente
    return send_file(f"./audios/{nombreAudio}", mimetype="audio/mpeg")

@apis.route("/api/twilio/respuesta", methods=["POST"])
def procesarRespuestaLlamada():
    speech = request.form.get("SpeechResult")
    confidence = request.form.get("Confidence")
    return LlamadasController.procesarRespuesta(speech, confidence)

@apis.route("/api/llamadas", methods=["POST"])
def generarLlamada():
    data = request.get_json()
    return LlamadasController.llamar(data)

@apis.route("/api/twilio/accion", methods=["POST"])
def generarAccionesEnLlamada():
    return LlamadasController.generarAccionesEnLlamada()

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
@apis.route("/api/mensajes/whatsapp-twilio", methods=["POST"])
def enviarMensajeWhatsappTwilio():
    data = request.get_json()
    return MensajesController.enviarMensajeWhatsapp(data)

@apis.route("/api/mensajes/sms", methods=["POST"])
def enviarMensajeSMS():
    data = request.get_json()
    return MensajesController.enviarMensajeSMS(data)

@apis.route("/api/mensajes/whatsapp-selenium", methods=["POST"])
def enviarMensajeWhatsappSelenium():
    data = request.get_json()
    return MensajesController.enviarMensajeWhatsappSelenium(data)

@apis.route("/api/mensajes/whatsapp-whapi", methods=["POST"])
def enviarMensajeWhatsappWhapi():
    data = request.get_json()
    return MensajesController.enviarMensajeWhapiCloud(data)

@apis.route("/api/mensajes/whatsapp-grupo-whapi", methods=["POST"])
def enviarMensajeWhatsappGrupoWhapi():
    data = request.get_json()
    return MensajesController.enviarMensajeWhapiGrupo(data)

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
@apis.route("/api/email/enviar-id", methods=["POST"]) # Esta ruta
def enviarEmailPorID():
    data = request.get_json()
    return EmailController.enviarMailPorID(data)

@apis.route("/api/email/generar", methods=["POST"]) # Esta ruta llama a gemini y genera un asunto y texto en html
def llamarIAGemini():
    data = request.get_json()
    return AIController.armarEmail(data)

@apis.route("/api/email/notificar", methods=["POST"]) # Esta ruta envia una notificacion con el email de PhishIntel
def notificarViaEmail():
    data = request.get_json()
    return EmailController.enviarNotificacionPhishintel(data)

@apis.route("/api/email/enviar", methods=["POST"]) # Esta ruta
def enviarEmail():
    data = request.get_json()
    return EmailController.enviarMail(data)

@apis.route("/api/email/generar-enviar", methods=["POST"])
def generarYEnviarEmail():
    data = request.get_json()
    return EmailController.generarYEnviarMail(data)

# ------ # MENSAJES # ------ #
@apis.route("/api/mensaje/generar", methods=["POST"]) # Esta ruta llama a gemini y genera un mensaje de WhatsApp
def generarMensaje():
    data = request.get_json()
    return AIController.armarMensaje(data)

@apis.route("/api/mensaje/enviar-id", methods=["POST"]) # Esta ruta envía un mensaje por ID de usuario
def enviarMensajePorID():
    data = request.get_json()
    return MensajesController.enviarMensajePorID(data)

# ------ # TELEGRAM BOT # ------ #
@apis.route("/api/telegram/start", methods=["POST"]) # Inicia el bot de Telegram
def iniciarBotTelegram():
    import asyncio
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(telegram_bot.start_bot())
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"mensaje": f"Error al iniciar el bot: {str(e)}", "status": "error"}), 500

@apis.route("/api/telegram/stop", methods=["POST"]) # Detiene el bot de Telegram
def detenerBotTelegram():
    import asyncio
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(telegram_bot.stop_bot())
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"mensaje": f"Error al detener el bot: {str(e)}", "status": "error"}), 500

@apis.route("/api/telegram/status", methods=["GET"]) # Obtiene el estado del bot y usuarios registrados
def estadoBotTelegram():
    try:
        status = telegram_bot.get_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"mensaje": f"Error al obtener estado: {str(e)}", "status": "error"}), 500

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

@apis.route("/api/usuarios/batch", methods=["POST"])
def crearUsuariosBatch():
    data = request.get_json()
    return UsuariosController.crearUsuariosBatch(data)

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

@apis.route("/api/areas/batch", methods=["POST"])
def crearAreasBatch():
    data = request.get_json()
    return AreasController.crearAreasBatch(data)

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

# ------ # AREAS - REPORTES # ------ #
@apis.route("/api/areas/fallas", methods=["GET"])
def obtenerFallasPorArea():
    from app.backend.models.tipoEvento import TipoEvento
    
    # Obtener parámetros de filtro por tipos de evento (múltiples)
    tipos_evento_params = request.args.getlist('tipo_evento')
    tipos_evento = []
    
    if tipos_evento_params:
        # Mapear los valores del frontend a los enums
        tipo_mapping = {
            'CORREO': TipoEvento.CORREO,
            'MENSAJE': TipoEvento.MENSAJE,
            'LLAMADA': TipoEvento.LLAMADA,
            'VIDEOLLAMADA': TipoEvento.VIDEOLLAMADA
        }
        tipos_evento = [tipo_mapping.get(tipo.upper()) for tipo in tipos_evento_params if tipo_mapping.get(tipo.upper())]
    
    return AreasController.obtenerFallasPorArea(tipos_evento if tipos_evento else None)

@apis.route("/api/areas/fallas-fecha", methods=["GET"])
def obtenerFallasPorFecha():
    from app.backend.models.tipoEvento import TipoEvento
    
    # Obtener parámetros de filtro (múltiples)
    tipos_evento_params = request.args.getlist('tipo_evento')
    periodos_params = request.args.getlist('periodo')
    
    tipos_evento = []
    periodos = []
    
    if tipos_evento_params:
        tipo_mapping = {
            'CORREO': TipoEvento.CORREO,
            'MENSAJE': TipoEvento.MENSAJE,
            'LLAMADA': TipoEvento.LLAMADA,
            'VIDEOLLAMADA': TipoEvento.VIDEOLLAMADA
        }
        tipos_evento = [tipo_mapping.get(tipo.upper()) for tipo in tipos_evento_params if tipo_mapping.get(tipo.upper())]
    
    if periodos_params:
        periodos = periodos_params
    
    return AreasController.obtenerFallasPorFecha(
        periodos if periodos else None, 
        tipos_evento if tipos_evento else None
    )