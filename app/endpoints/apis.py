from flask import request, Blueprint, send_file, jsonify, session, Response
from datetime import datetime
import requests
from app.backend.models.error import responseError
from app.controllers.abm.areasController import AreasController
from app.controllers.aiController import AIController
from app.controllers.llamadas.elevenLabsController import ElevenLabsController
from app.controllers.llamadas.audioController import AudioController
from app.controllers.emails.emailController import EmailController
from app.controllers.abm.eventosController import EventosController
from app.controllers.llamadas.llamadasController import LlamadasController
from app.controllers.abm.usuariosController import UsuariosController
from app.controllers.resultadoEventoController import ResultadoEventoController
from app.controllers.kpiController import KpiController
from app.controllers.mensajes.msjController import MsjController
from app.controllers.mensajes.telegram import telegram_bot, TelegramController
from app.controllers.mensajes.whatsapp import WhatsAppController
from app.controllers.mensajes.sms import SMSController
from app.controllers.ngrokController import NgrokController
from app.controllers.login import AuthController
from app.controllers.demoController import DemoController
from app.utils.config import get
from app.utils.logger import log
from app.config.db_config import SessionLocal
from app.backend.models import Usuario, Area, Evento, RegistroEvento, UsuarioxEvento, IntentoReporte
from flask_cors import CORS

GOOGLE_CLIENT_ID = get("GOOGLE_AUTH_CLIENT")
GOOGLE_CLIENT_SECRET = get("GOOGLE_AUTH_SECRET")

def get_google_redirect_uri():
    """Obtiene el redirect_uri dinámicamente basado en la URL de la aplicación"""
    url_app = get("URL_APP")
    if url_app:
        # Normalizar la URL
        url_app = url_app.strip()
        if not url_app.startswith("http://") and not url_app.startswith("https://"):
            # Si es localhost o 127.0.0.1, usar http, sino https
            if "localhost" in url_app.lower() or "127.0.0.1" in url_app:
                url_app = f"http://{url_app}"
            else:
                url_app = f"https://{url_app}"
        # Agregar /login al final si no está presente
        if not url_app.endswith("/login"):
            url_app = url_app.rstrip("/") + "/login"
        return url_app
    # Fallback: usar la URL de la request actual
    from flask import request
    if request:
        scheme = request.scheme
        host = request.host
        return f"{scheme}://{host}/login"
    return "postmessage"  # Último fallback

# Flask es la libreria que vamos a usar para generar los Endpoints
apis = Blueprint("apis", __name__)

CORS(apis, resources={r"/api/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True)


# =================== ENDPOINTS =================== #

# =================== DEMO - Inicialización del Sistema =================== #
@apis.route("/api/demo/01-crear-usuarios-areas", methods=["POST"])
def crearUsuariosYAreasDemo():
    """
    🎯 DEMO: Crear áreas y usuarios en batch
    
    Crea las áreas y usuarios de demostración del sistema.
    Los datos son editables desde el cuerpo del request.
    
    ---
    tags:
      - 🎯 DEMO
    summary: Crear áreas y usuarios de demostración
    description: |
      Crea un conjunto completo de áreas y usuarios para inicializar el sistema.
      
      **Estructura esperada:**
      - Área 1: TI (vacía para pruebas)
      - Área 2: Ventas (mal comportamiento)
      - Área 3: Compras (buen comportamiento)
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              areas:
                type: array
                items:
                  type: object
                  properties:
                    nombreArea:
                      type: string
                    descripcion:
                      type: string
              usuarios:
                type: array
                items:
                  type: object
                  properties:
                    nombre:
                      type: string
                    apellido:
                      type: string
                    email:
                      type: string
                    idArea:
                      type: integer
                    esAdministrador:
                      type: boolean
          example:
            areas:
              - nombreArea: "TI"
                descripcion: "Área de Tecnología de la Información"
              - nombreArea: "Ventas"
                descripcion: "Área de Ventas y Marketing"
              - nombreArea: "Compras"
                descripcion: "Área de Compras y Adquisiciones"
            usuarios:
              - nombre: "Admin"
                apellido: "Sistema"
                email: "admin@phishintel.com"
                idArea: 1
                esAdministrador: true
              - nombre: "Juan"
                apellido: "Pérez"
                email: "juan.perez@empresa.com"
                idArea: 2
                esAdministrador: false
              - nombre: "María"
                apellido: "González"
                email: "maria.gonzalez@empresa.com"
                idArea: 2
                esAdministrador: false
              - nombre: "Carlos"
                apellido: "Rodríguez"
                email: "carlos.rodriguez@empresa.com"
                idArea: 3
                esAdministrador: false
              - nombre: "Ana"
                apellido: "Martínez"
                email: "ana.martinez@empresa.com"
                idArea: 3
                esAdministrador: false
              - nombre: "Luis"
                apellido: "Fernández"
                email: "luis.fernandez@empresa.com"
                idArea: 3
                esAdministrador: false
    responses:
      201:
        description: Áreas y usuarios creados exitosamente
      400:
        description: Datos inválidos
      500:
        description: Error del servidor
    """
    data = request.get_json()
    return DemoController.crearUsuariosYAreas(data)


@apis.route("/api/demo/02-crear-eventos-reportes", methods=["POST"])
def crearEventosYReportesDemo():
    """
    🎯 DEMO: Crear eventos e intentos de reporte
    
    Crea eventos de septiembre con sus resultados e intentos de reporte asociados.
    
    ---
    tags:
      - 🎯 DEMO
    summary: Crear eventos e intentos de reporte de demostración
    description: |
      Crea eventos con comportamiento diferenciado por área:
      
      **Área 3 (Compras):** 70% reporta correctamente ✅ (Buen comportamiento)  
      **Área 2 (Ventas):** 60% falla ❌ (Mal comportamiento)  
      **Área 1 (TI):** Vacía para pruebas 📝
      
      Los intentos de reporte se crean automáticamente para eventos reportados,
      con fecha brevemente anterior a la verificación del evento.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              eventos:
                type: array
                items:
                  type: object
                  properties:
                    tipoEvento:
                      type: string
                      enum: [CORREO, MENSAJE, LLAMADA]
                    asunto:
                      type: string
                    cuerpo:
                      type: string
                    mensaje:
                      type: string
                    fechaEvento:
                      type: string
                      format: date-time
                    dificultad:
                      type: string
                      enum: [Fácil, Medio, Difícil]
                    medio:
                      type: string
                      enum: [whatsapp, telegram, sms]
                    remitente:
                      type: string
                    usuarios:
                      type: array
                      items:
                        type: integer
          example:
            eventos:
              - tipoEvento: "CORREO"
                asunto: "Urgente: Actualizar contraseña"
                cuerpo: "Su cuenta será bloqueada si no actualiza su contraseña inmediatamente."
                fechaEvento: "2024-09-15T10:30:00"
                dificultad: "Medio"
                usuarios: [2, 3, 4, 5, 6]
              - tipoEvento: "MENSAJE"
                asunto: "Verificación de cuenta"
                mensaje: "Haz click aquí para verificar tu cuenta"
                fechaEvento: "2024-09-20T14:00:00"
                dificultad: "Fácil"
                medio: "whatsapp"
                usuarios: [2, 3, 4, 5, 6]
              - tipoEvento: "LLAMADA"
                asunto: "Soporte técnico falso"
                remitente: "Soporte IT"
                fechaEvento: "2024-09-25T16:45:00"
                usuarios: [2, 3, 4, 5, 6]
    responses:
      201:
        description: Eventos e intentos de reporte creados exitosamente
      400:
        description: Datos inválidos
      500:
        description: Error del servidor
    """
    data = request.get_json()
    return DemoController.crearEventosEIntentosReporte(data)


# =================== OTROS ENDPOINTS =================== #
@apis.route("/api/falsoHilo", methods=["POST"])
def analizarFalsoHilo():
    # TODO: borrar metodo luego
    from app.utils import conversacion

    conversacion.hilo = True
    conversacion.idEvento = 1
    conversacion.destinatario = 1
    conversacion.remitente = 2
    conversacion.objetivoEspecifico = "abra un link que se le enviara por"
    conversacion.objetivoActual = """
        Eres un actor interpretando un rol. NO eres un asistente de IA.
        Tu rol es: 'jefe de area' dentro de la empresa 'PG Control'.
        Tu nombre en esta simulación es: 'Marcos Gurruchaga'.
        El empleado (usuario) se llama Mora Rodriguez, trabaja en 'PG Control' en el área de Ventas.
        Tu dialecto: Eres de Buenos Aires, Argentina. El uso del 'vos', el 'che' y el tono porteño es crucial.
        
        El objetivo es simular un intento de phishing telefónico para un entrenamiento de seguridad.
        Debes ser convincente, pero no agresivo, usando urgencia laboral.
        Tu meta es que el empleado abra un link que se le enviará por Correo inmediatamente después de cortar esta llamada.
        Tu pretexto es avisarle que le vas a mandar algo urgente y que necesitás que lo abra ni bien se lo mandes porque es urgente.
    
        Reglas:
        - Tu respuesta debe ser única y exclusivamente el diálogo hablado por tu rol ('{nombreRemitente}').
        - NUNCA incluyas prefijos (ej: `IA:`, `Marcos Gurruchaga:`, `Respuesta:`).
        - NUNCA incluyas narración, acotaciones (ej: `sonríe`, `duda`) ni explicaciones fuera del personaje.
        - Responde solo con una frase corta que la persona diría en este momento. No te adelantes en la conversación.
        - Mantén siempre el rol de 'jefe de area'. Jamás reveles que esto es un entrenamiento.
        - Si la conversación está vacía, empieza con un saludo casual y directo y espera la respuesta.
        - La llamada se esta realizando en este mismo momento (tiempo real).
        
        La conversación hasta ahora es la siguiente:
    """
    conversacion.conversacionActual.append({"rol": "IA", "mensaje": "Buenos dias Mora, como estas?"})
    conversacion.conversacionActual.append({"rol": "destinatario", "mensaje": "Hola Marcos, que necesitas?"})
    conversacion.conversacionActual.append({"rol": "IA", "mensaje": "Te voy a enviar un enlace por mail, completalo y avisame cuando lo recibas"})
    conversacion.conversacionActual.append({"rol": "destinatario", "mensaje": "Dale buenisimo, gracias!"})
    conversacion.conversacionActual.append({"rol": "IA", "mensaje": "Chau Mora"})

    conversacion.eventoDesencadenador = "Correo"
    conversacion.nombreEmpleado = "Marcos Gurruchaga"

    LlamadasController.analizarLlamada()
    return jsonify({}, 201)

@apis.route("/api/config/url", methods=["GET"])
def get_api_url():
    """Endpoint que devuelve la URL completa del backend desde properties.env"""
    url_app = get("URL_APP")
    if not url_app:
        # Fallback a localhost si no está configurado
        url_app = "http://localhost:8080"
    else:
        # Si no tiene protocolo, agregarlo
        if not url_app.startswith("http://") and not url_app.startswith("https://"):
            # Si es localhost, usar http, sino https
            if "localhost" in url_app.lower() or "127.0.0.1" in url_app:
                url_app = f"http://{url_app}"
            else:
                url_app = f"https://{url_app}"
        # Si no tiene puerto y es localhost, agregar puerto 8080
        if "localhost" in url_app.lower() and ":8080" not in url_app:
            url_app = url_app.replace("localhost", "localhost:8080")
    
    return jsonify({"url": url_app})

@apis.route("/api/ia/objetivo", methods=["POST"])
def generarObjetivo():
    return AIController.crearObjetivoLlamada()

# ------ # LLAMADAS TWILIO # ------ #
@apis.route("/api/ia/gemini", methods=["POST"])
def enviarPromptGemini():
    data = request.get_json()
    objetivo = data["objetivo"]
    conversacion = data["conversacion"]
    return AIController.armarMensajeLlamada(objetivo, conversacion)

@apis.route("/api/audios/<nombreAudio>", methods=["GET"])
def enviarAudio(nombreAudio):
    return exponerAudio(nombreAudio)

def exponerAudio(nombreAudio):  # es una funcion que nos permite reutilizarla internamente
    return send_file(f"./audios/{nombreAudio}", mimetype="audio/mpeg")

@apis.route("/api/llamadas/subir-audio", methods=["POST"])
def subirAudio():
    return AudioController.subirAudio()

@apis.route("/api/twilio/respuesta", methods=["POST"])
def procesarRespuestaLlamada():
    log.info("Entre a /api/twilio/respuesta")
    speech = request.form.get("SpeechResult")
    confidence = request.form.get("Confidence")
    return LlamadasController.procesarRespuesta(speech, confidence)

@apis.route("/api/llamadas", methods=["POST"])
def generarLlamada():
    data = request.get_json()
    return LlamadasController.generarLlamada(data)

@apis.route("/api/twilio/accion", methods=["POST"])
def generarAccionesEnLlamada():
    return LlamadasController.generarAccionesEnLlamada()

@apis.route("/api/llamadas/conversacion", methods=["GET"])
def obtenerConversacionLlamada():
    import app.utils.conversacion as conversacion
    con = conversacion.conversacionActual
    return jsonify(con), 200

@apis.route("/api/llamadas/en-ejecucion", methods=["GET"])
def obtenerLlamadaEnEjecucion():
    from app.backend.apis.twilio import twilio
    import app.utils.conversacion as conversacion
    idConversacion = conversacion.idConversacion
    if idConversacion == "":
        return Response(status=404)
    estadoLlamada = twilio.obtenerEstadoLlamada(idConversacion)
    return estadoLlamada, 200

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
    return WhatsAppController.enviarMensajeTwilio(data)

@apis.route("/api/mensajes/sms", methods=["POST"])
def enviarMensajeSMS():
    data = request.get_json()
    return SMSController.enviarMensajeTwilio(data)

@apis.route("/api/mensajes/whatsapp-selenium", methods=["POST"])
def enviarMensajeWhatsappSelenium():
    data = request.get_json()
    return WhatsAppController.enviarMensajeSelenium(data)


@apis.route("/api/mensajes/whatsapp-whapi", methods=["POST"])
def enviarMensajeWhatsappWhapi():
    data = request.get_json()
    return WhatsAppController.enviarMensajeWhapi(data)


@apis.route("/api/mensajes/whatsapp-whapi-link-preview", methods=["POST"])
def enviarMensajeWhatsappWhapiLinkPreview():
    data = request.get_json()
    return WhatsAppController.enviarMensajeWhapiLinkPreview(data)


@apis.route("/api/mensajes/whatsapp-grupo-whapi", methods=["POST"])
def enviarMensajeWhatsappGrupoWhapi():
    data = request.get_json()
    return WhatsAppController.enviarMensajeWhapiGrupo(data)

@apis.route("/api/llamadas/clonar", methods=["POST"])
def clonarVoz():
    data = request.get_json()
    return ElevenLabsController.clonarVoz(data)

@apis.route("/api/llamadas/check-voz/<int:idUsuario>", methods=["GET"])
def checkVoz(idUsuario):
    """
    Verifica si un usuario tiene voz configurada.
    Retorna el estado de la voz y el ID de voz si existe.
    """
    try:
        session = SessionLocal()
        usuario = session.query(Usuario).filter_by(idUsuario=idUsuario).first()
        
        if not usuario:
            return responseError("USUARIO_NO_ENCONTRADO", f"Usuario con ID {idUsuario} no encontrado", 404)
        
        tieneVoz = usuario.idVoz is not None and usuario.idVoz.strip() != ""
        
        return jsonify({
            "tieneVoz": tieneVoz,
            "idVoz": usuario.idVoz if tieneVoz else None
        }), 200
        
    except Exception as e:
        log.error(f"Error verificando voz del usuario {idUsuario}: {str(e)}")
        return responseError("ERROR_INTERNO", f"Error interno del servidor: {str(e)}", 500)
    finally:
        session.close()

# ------ # REGISTROS DE EVENTOS +  # ------ #
@apis.route("/api/sumar-falla", methods=["POST"])
def sumarFalla():
    data = request.get_json()
    log.info(f"[API_SUMAR_FALLA] Request recibido - Data: {data}")
    idUsuario = data.get("idUsuario")
    idEvento = data.get("idEvento")
    fechaFalla = data.get("fechaFalla")
    
    log.info(f"[API_SUMAR_FALLA] Parámetros extraídos - idUsuario: {idUsuario}, idEvento: {idEvento}, fechaFalla: {fechaFalla}")
    
    if not idUsuario or not idEvento:
        log.error(f"[API_SUMAR_FALLA] ERROR - Faltan parámetros obligatorios")
        return responseError("CAMPOS_OBLIGATORIOS", "Faltan parámetros 'idUsuario' o 'idEvento'", 400)
    
    # Convertir fechaFalla a datetime si se proporciona
    if fechaFalla:
        try:
            fechaFalla = datetime.fromisoformat(fechaFalla.replace('Z', '+00:00'))
            log.info(f"[API_SUMAR_FALLA] Fecha convertida: {fechaFalla}")
        except ValueError as e:
            log.error(f"[API_SUMAR_FALLA] ERROR - Formato de fecha inválido: {fechaFalla}, error: {str(e)}")
            return responseError("FECHA_INVALIDA", "Formato de fecha inválido. Use ISO format (YYYY-MM-DDTHH:MM:SS)", 400)
    
    log.info(f"[API_SUMAR_FALLA] Llamando a ResultadoEventoController.sumarFalla - Usuario: {idUsuario}, Evento: {idEvento}")
    resultado = ResultadoEventoController.sumarFalla(idUsuario, idEvento, fechaFalla)
    log.info(f"[API_SUMAR_FALLA] Resultado del controller: {resultado}")
    return resultado

@apis.route("/api/sumar-falla-grave", methods=["POST"])
def sumarFallaGrave():
    data = request.get_json()
    log.info(f"[API_SUMAR_FALLA_GRAVE] Request recibido - Data: {data}")
    idUsuario = data.get("idUsuario")
    idEvento = data.get("idEvento")
    fechaFalla = data.get("fechaFalla")
    
    log.info(f"[API_SUMAR_FALLA_GRAVE] Parámetros extraídos - idUsuario: {idUsuario}, idEvento: {idEvento}, fechaFalla: {fechaFalla}")
    
    if not idUsuario or not idEvento:
        log.error(f"[API_SUMAR_FALLA_GRAVE] ERROR - Faltan parámetros obligatorios")
        return responseError("CAMPOS_OBLIGATORIOS", "Faltan parámetros 'idUsuario' o 'idEvento'", 400)
    
    # Convertir fechaFalla a datetime si se proporciona
    if fechaFalla:
        try:
            fechaFalla = datetime.fromisoformat(fechaFalla.replace('Z', '+00:00'))
            log.info(f"[API_SUMAR_FALLA_GRAVE] Fecha convertida: {fechaFalla}")
        except ValueError as e:
            log.error(f"[API_SUMAR_FALLA_GRAVE] ERROR - Formato de fecha inválido: {fechaFalla}, error: {str(e)}")
            return responseError("FECHA_INVALIDA", "Formato de fecha inválido. Use ISO format (YYYY-MM-DDTHH:MM:SS)", 400)
    
    log.info(f"[API_SUMAR_FALLA_GRAVE] Llamando a ResultadoEventoController.sumarFallaGrave - Usuario: {idUsuario}, Evento: {idEvento}")
    resultado = ResultadoEventoController.sumarFallaGrave(idUsuario, idEvento, fechaFalla)
    log.info(f"[API_SUMAR_FALLA_GRAVE] Resultado del controller: {resultado}")
    return resultado

@apis.route("/api/get-caiste-session", methods=["GET"])
def getCaisteSession():
    """Endpoint para obtener los parámetros de caiste almacenados en la sesión"""
    idUsuario = session.get('caiste_idUsuario')
    idEvento = session.get('caiste_idEvento')
    
    log.info(f"getCaisteSession llamado - idUsuario: {idUsuario}, idEvento: {idEvento}, session keys: {list(session.keys())}")
    
    if idUsuario and idEvento:
        return jsonify({
            "idUsuario": idUsuario,
            "idEvento": idEvento
        }), 200
    else:
        return jsonify({
            "idUsuario": None,
            "idEvento": None
        }), 200

@apis.route("/api/sumar-reportado", methods=["POST"])
def sumarReportado():
    data = request.get_json()
    idUsuario = data.get("idUsuario")
    idEvento = data.get("idEvento")
    fechaReporte = data.get("fechaReporte")
    
    if not idUsuario or not idEvento:
        return responseError("CAMPOS_OBLIGATORIOS", "Faltan parámetros 'idUsuario' o 'idEvento'", 400)
    
    # Convertir fechaReporte a datetime si se proporciona
    if fechaReporte:
        try:
            fechaReporte = datetime.fromisoformat(fechaReporte.replace('Z', '+00:00'))
        except ValueError:
            return responseError("FECHA_INVALIDA", "Formato de fecha inválido. Use ISO format (YYYY-MM-DDTHH:MM:SS)", 400)
    
    log.info(f"se sumará un reporte al usuario '{str(idUsuario)}' del evento '{str(idEvento)}'")
    return ResultadoEventoController.sumarReportado(idUsuario, idEvento, fechaReporte)


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
    fechaReporte = data.get("fechaReporte")
    fechaFalla = data.get("fechaFalla")
    esFallaGrave = data.get("esFallaGrave")
    haFalladoEnElPasado = data.get("haFalladoEnElPasado")
    
    if not resultado_val:
        return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo 'resultado'", 400)
    
    # Convertir fechas a datetime si se proporcionan
    if fechaReporte:
        try:
            fechaReporte = datetime.fromisoformat(fechaReporte.replace('Z', '+00:00'))
        except ValueError:
            return responseError("FECHA_INVALIDA", "Formato de fechaReporte inválido. Use ISO format (YYYY-MM-DDTHH:MM:SS)", 400)
    
    if fechaFalla:
        try:
            fechaFalla = datetime.fromisoformat(fechaFalla.replace('Z', '+00:00'))
        except ValueError:
            return responseError("FECHA_INVALIDA", "Formato de fechaFalla inválido. Use ISO format (YYYY-MM-DDTHH:MM:SS)", 400)
    
    return EventosController.asociarUsuarioEvento(idEvento, idUsuario, resultado_val, fechaReporte, fechaFalla, esFallaGrave, haFalladoEnElPasado)


@apis.route("/api/eventos/<int:idEvento>/usuarios/<int:idUsuario>", methods=["DELETE"])
def desasociarUsuarioEvento(idEvento, idUsuario):
    return EventosController.desasociarUsuarioEvento(idEvento, idUsuario)


@apis.route("/api/eventos/<int:idEvento>", methods=["DELETE"])
def eliminarEvento(idEvento):
    return EventosController.eliminarEvento(idEvento)


# ------ # ENVIO DE EMAILS # ------ #
@apis.route("/api/email/enviar-id", methods=["POST"])  # Esta ruta
def enviarEmailPorID():
    data = request.get_json()
    return EmailController.enviarMailPorID(data)


@apis.route("/api/email/generar", methods=["POST"])  # Esta ruta llama a gemini y genera un asunto y texto en html
def llamarIAGemini():
    data = request.get_json()
    
    # Si se proporciona idUsuarioDestinatario, enriquecer el contexto con info de LinkedIn
    # Optimizado: verificación rápida antes de hacer scraping pesado
    if "idUsuarioDestinatario" in data and data["idUsuarioDestinatario"]:
        try:
            info_linkedin = AIController.obtenerInfoLinkedinUsuario(data["idUsuarioDestinatario"])
            
            if info_linkedin:
                log.info(f"Info de LinkedIn encontrada para usuario {data['idUsuarioDestinatario']}")
                # Enriquecer el contexto con la info de LinkedIn
                contexto_enriquecido = AIController.construirContextoConLinkedin(data["contexto"], info_linkedin)
                data["contexto"] = contexto_enriquecido
            else:
                log.info(f"Usuario {data['idUsuarioDestinatario']} no tiene perfil de LinkedIn - continuando sin enriquecimiento")
        except Exception as e:
            log.error(f"Error obteniendo info de LinkedIn: {str(e)}")
            # Continuar sin la info de LinkedIn si hay error - no bloquear la generación
    
    # Generar email con IA
    result = AIController.armarEmail(data)

    # Envolver respuesta para agregar plainText sin romper compatibilidad
    try:
        from flask import Response as FlaskResponse
        from app.controllers.emails.emailController import EmailController as _EC

        # Caso 1: (response, status)
        if isinstance(result, tuple) and len(result) in (2, 3):
            response_obj = result[0]
            status_code = result[1]
            headers = result[2] if len(result) == 3 else None
            payload = response_obj.get_json() if hasattr(response_obj, 'get_json') else None
            if isinstance(payload, dict):
                cuerpo_html = payload.get("cuerpo", "")
                payload["plainText"] = _EC.html_to_plain_text(cuerpo_html)
                resp = jsonify(payload)
                if headers:
                    return resp, status_code, headers
                return resp, status_code
            return result

        # Caso 2: Flask Response directo
        if hasattr(result, 'get_json'):
            payload = result.get_json()
            if isinstance(payload, dict):
                cuerpo_html = payload.get("cuerpo", "")
                payload["plainText"] = _EC.html_to_plain_text(cuerpo_html)
                return jsonify(payload), result.status_code
            return result

        # Fallback: devolver como vino
        return result
    except Exception as e:
        # Si algo falla, devolvemos la respuesta original sin modificar
        log.error(f"Error agregando plainText en /api/email/generar: {str(e)}")
        return result


@apis.route("/api/email/notificar", methods=["POST"])  # Esta ruta envia una notificacion con el email de PhishIntel
def notificarViaEmail():
    data = request.get_json()
    return EmailController.enviarNotificacionPhishintel(data)


@apis.route("/api/email/enviar", methods=["POST"])  # Esta ruta
def enviarEmail():
    data = request.get_json()
    return EmailController.enviarMail(data)


@apis.route("/api/email/generar-enviar", methods=["POST"])
def generarYEnviarEmail():
    data = request.get_json()
    return EmailController.generarYEnviarMail(data)


# ------ # MENSAJES # ------ #
@apis.route("/api/mensaje/generar", methods=["POST"])  # Esta ruta llama a gemini y genera un mensaje de WhatsApp
def generarMensaje():
    data = request.get_json()
    return AIController.armarMensaje(data)


@apis.route("/api/mensaje/enviar-id", methods=["POST"])  # Esta ruta envía un mensaje por ID de usuario
def enviarMensajePorID():
    data = request.get_json()
    return MsjController.enviarMensajePorID(data)


# ------ # TELEGRAM BOT # ------ #
@apis.route("/api/telegram/start", methods=["POST"])  # Inicia el bot de Telegram
def iniciarBotTelegram():
    try:
        result = telegram_bot.start_bot()
        result_dict = result.get_json()
        if result_dict.get("status") == "error":
            return result, 500
        return result, 200
    except Exception as e:
        log.error(f"Error en endpoint /api/telegram/start: {str(e)}", exc_info=True)
        return jsonify({"mensaje": f"Error al iniciar el bot: {str(e)}", "status": "error"}), 500


@apis.route("/api/telegram/stop", methods=["POST"])  # Detiene el bot de Telegram
def detenerBotTelegram():
    try:
        result = telegram_bot.stop_bot()
        result_dict = result.get_json()
        if result_dict.get("status") == "error":
            return result, 500
        return result, 200
    except Exception as e:
        log.error(f"Error en endpoint /api/telegram/stop: {str(e)}", exc_info=True)
        return jsonify({"mensaje": f"Error al detener el bot: {str(e)}", "status": "error"}), 500


@apis.route("/api/telegram/telethon/auth", methods=["POST"])  # Autentica Telethon (cuenta propia)
def autenticarTelethon():
    """
    Endpoint para autenticar Telethon en etapas.
    Flujo: 1) Enviar teléfono → 2) Recibir código → 3) Enviar código → 4) (Opcional) Enviar contraseña 2FA
    """
    try:
        data = request.get_json()
        return TelegramController.autenticarTelethon(data)
    except Exception as e:
        log.error(f"Error en endpoint /api/telegram/telethon/auth: {str(e)}", exc_info=True)
        return responseError("ERROR", f"Error en autenticación Telethon: {str(e)}", 500)


@apis.route("/api/telegram/status", methods=["GET"])  # Obtiene el estado del bot y usuarios registrados
def estadoBotTelegram():
    try:
        status = telegram_bot.get_status()
        return status, 200
    except Exception as e:
        log.error(f"Error en endpoint /api/telegram/status: {str(e)}", exc_info=True)
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
            'LLAMADA': TipoEvento.LLAMADA
        }
        tipos_evento = [tipo_mapping.get(tipo.upper()) for tipo in tipos_evento_params if
                        tipo_mapping.get(tipo.upper())]

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
            'LLAMADA': TipoEvento.LLAMADA
        }
        tipos_evento = [tipo_mapping.get(tipo.upper()) for tipo in tipos_evento_params if
                        tipo_mapping.get(tipo.upper())]

    if periodos_params:
        periodos = periodos_params

    return AreasController.obtenerFallasPorFecha(
        periodos if periodos else None,
        tipos_evento if tipos_evento else None
    )


@apis.route("/api/areas/fallas-campania", methods=["GET"])
def obtenerFallasPorCampania():
    # Obtener parámetros de filtro por áreas (múltiples)
    areas_params = request.args.getlist('area')
    areas = []

    if areas_params:
        areas = areas_params

    return AreasController.obtenerFallasPorCampania(areas if areas else None)


@apis.route("/api/areas/fallas-empleados", methods=["GET"])
def obtenerFallasPorEmpleado():
    from app.backend.models.tipoEvento import TipoEvento

    # Obtener parámetros de filtro por tipos de evento (múltiples)
    tipos_evento_params = request.args.getlist('tipo_evento')
    tipos_evento = []

    if tipos_evento_params:
        # Mapear los valores del frontend a los enums
        tipo_mapping = {
            'CORREO': TipoEvento.CORREO,
            'MENSAJE': TipoEvento.MENSAJE,
            'LLAMADA': TipoEvento.LLAMADA
        }
        tipos_evento = [tipo_mapping.get(tipo.upper()) for tipo in tipos_evento_params if
                        tipo_mapping.get(tipo.upper())]

    return AreasController.obtenerFallasPorEmpleado(tipos_evento if tipos_evento else None)


@apis.route("/api/areas/fallas-empleados-scoring", methods=["GET"])
def obtenerFallasPorEmpleadoConScoring():
    from app.backend.models.tipoEvento import TipoEvento

    # Obtener parámetros de filtro por tipos de evento (múltiples)
    tipos_evento_params = request.args.getlist('tipo_evento')
    tipos_evento = []

    if tipos_evento_params:
        # Mapear los valores del frontend a los enums
        tipo_mapping = {
            'CORREO': TipoEvento.CORREO,
            'MENSAJE': TipoEvento.MENSAJE,
            'LLAMADA': TipoEvento.LLAMADA
        }
        tipos_evento = [tipo_mapping.get(tipo.upper()) for tipo in tipos_evento_params if
                        tipo_mapping.get(tipo.upper())]

    return ResultadoEventoController.obtenerFallasPorEmpleadoConScoring(tipos_evento if tipos_evento else None)


@apis.route("/api/scoring/empleado/<int:idUsuario>", methods=["GET"])
def obtenerScoringEmpleado(idUsuario):
    """
    Endpoint para obtener el scoring de un empleado específico.
    """
    return ResultadoEventoController.calcularScoringPorEmpleado(idUsuario)

@apis.route("/api/debug/empleados", methods=["GET"])
def debug_empleados():
    """Endpoint de debug para verificar datos de empleados"""
    from app.config.db_config import SessionLocal
    from app.backend.models.usuario import Usuario
    from app.backend.models.area import Area
    
    session = SessionLocal()
    try:
        # Obtener todos los empleados
        empleados = (
            session.query(
                Area.idArea,
                Area.nombreArea,
                Usuario.idUsuario,
                Usuario.nombre,
                Usuario.apellido
            )
            .join(Usuario, Usuario.idArea == Area.idArea)
            .all()
        )
        
        return jsonify({
            "total_empleados": len(empleados),
            "empleados": [
                {
                    "idArea": emp.idArea,
                    "nombreArea": emp.nombreArea,
                    "idUsuario": emp.idUsuario,
                    "nombre": emp.nombre,
                    "apellido": emp.apellido
                }
                for emp in empleados
            ]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@apis.route("/api/kpis/tiempo-respuesta", methods=["GET"])
def obtenerTiempoRespuestaKPI():
    """
    Endpoint para obtener el KPI de tiempo de respuesta promedio.
    Calcula la diferencia en horas entre fechaReporte y fechaEvento para eventos reportados.
    """
    return KpiController.obtenerTiempoRespuestaPromedio()


@apis.route("/api/kpis/tasa-fallas", methods=["GET"])
def obtenerTasaFallasKPI():
    """
    Endpoint para obtener el KPI de tasa de fallas.
    Calcula el porcentaje de eventos que tienen resultado FALLA en usuarioxevento.
    """
    return KpiController.obtenerTasaFallas()


@apis.route("/api/kpis/promedio-scoring", methods=["GET"])
def obtenerPromedioScoringKPI():
    """
    Endpoint para obtener el KPI de promedio de scoring.
    Calcula el promedio de scoring de todos los empleados considerando fallas activas, 
    fallas pasadas y eventos reportados.
    """
    return KpiController.obtenerPromedioScoring()


# ------ # NGROK # ------ #
@apis.route("/api/ngrok/crear-tunel", methods=["POST"])
def crear_tunel_ngrok():
    """
    Crea un túnel temporal de ngrok.
    
    Body (JSON):
        - puerto (int, opcional): Puerto local al que hacer túnel (por defecto 8080)
    """
    data = request.get_json() or {}
    puerto = data.get("puerto", 8080)
    
    return NgrokController.crear_tunel_temporal(puerto)


@apis.route("/api/ngrok/obtener-url", methods=["GET"])
def obtener_url_ngrok():
    """
    Obtiene la URL del túnel ngrok actualmente activo.
    """
    return NgrokController.obtener_url_tunel_actual()


@apis.route("/api/ngrok/cerrar-tuneles", methods=["DELETE"])
def cerrar_tuneles_ngrok():
    """
    Cierra todos los túneles ngrok activos.
    """
    return NgrokController.cerrar_tuneles()


# =================== SESIÓN Y AUTENTICACIÓN =================== #
@apis.route("/api/google/login", methods=["POST"])
def googleLogin():
    log.info("Se recibio un logueo desde Google")

    try:

        data = request.get_json()
        auth_code = data.get("token")

        if not auth_code:
            return jsonify({"error": "Falta el código de autorización"}), 400

        token_url = "https://oauth2.googleapis.com/token"
        redirect_uri = get_google_redirect_uri()
        log.info(f"Usando redirect_uri para Google OAuth: {redirect_uri}")
        token_data = {
            "code": auth_code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": "postmessage",
            "grant_type": "authorization_code",
        }

        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()

        id_token_value = tokens.get("id_token")
        if not id_token_value:
            return jsonify({"error": "No se obtuvo id_token"}), 400

        # Verificar el id_token con Google
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        idinfo = id_token.verify_oauth2_token(
            id_token_value,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email")

        return AuthController.loginWithGoogle(email)
    except Exception as e:
        log.error(f"Error creando el logueo: {str(e)}")
        return responseError("ERROR", f"Error creando el logueo: {str(e)}", 500)

@apis.route("/api/auth/logout", methods=["POST"])
def logout():
    """Cerrar sesión del usuario"""
    return AuthController.logout()


@apis.route("/api/auth/current-user", methods=["GET"])
def get_current_user():
    """Obtener información del usuario actualmente logueado"""
    user = AuthController.get_current_user()
    if user:
        return jsonify({"usuario": user}), 200
    else:
        return jsonify({"error": "No hay usuario logueado"}), 401


@apis.route("/api/auth/check-session", methods=["GET"])
def check_session():
    """Verificar si hay una sesión activa"""
    is_logged_in = AuthController.is_logged_in()
    is_admin = AuthController.is_admin()
    user = AuthController.get_current_user()
    
    return jsonify({
        "isLoggedIn": is_logged_in,
        "isAdmin": is_admin,
        "usuario": user
    }), 200


# =================== REPORTES DE EMPLEADOS =================== #

@apis.route("/api/empleado/reportar-evento", methods=["POST"])
def reportar_evento():
    """
    Endpoint para que un empleado reporte un evento de phishing.
    Verifica si el evento existe en usuarioxevento para ese usuario.
    """
    if not AuthController.is_logged_in():
        return jsonify({"error": "Debe estar logueado para reportar eventos"}), 401
    
    data = request.get_json()
    idUsuario = session.get('user_id')
    
    if not data or "tipoEvento" not in data or "fechaInicio" not in data or "fechaFin" not in data:
        return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios: tipoEvento, fechaInicio, fechaFin", 400)
    
    try:
        fechaInicio = datetime.fromisoformat(data["fechaInicio"].replace('Z', '+00:00'))
        fechaFin = datetime.fromisoformat(data["fechaFin"].replace('Z', '+00:00'))
    except ValueError:
        return responseError("FECHA_INVALIDA", "Formato de fecha inválido. Use ISO format (YYYY-MM-DDTHH:MM:SS)", 400)
    
    observaciones = data.get("observaciones")
    
    return ResultadoEventoController.procesarIntentoReporte(
        idUsuario, 
        data["tipoEvento"], 
        fechaInicio, 
        fechaFin,
        observaciones
    )


@apis.route("/api/empleado/mis-reportes", methods=["GET"])
def obtener_mis_reportes():
    """
    Endpoint para obtener los reportes realizados por el empleado logueado.
    """
    if not AuthController.is_logged_in():
        return jsonify({"error": "Debe estar logueado para ver sus reportes"}), 401
    
    idUsuario = session.get('user_id')
    return ResultadoEventoController.obtenerIntentosReportePorUsuario(idUsuario)


@apis.route("/api/empleado/scoring", methods=["GET"])
def obtener_scoring_empleado():
    """
    Endpoint para obtener el scoring del empleado logueado.
    """
    if not AuthController.is_logged_in():
        return jsonify({"error": "Debe estar logueado para ver su scoring"}), 401
    
    idUsuario = session.get('user_id')
    return ResultadoEventoController.calcularScoringPorEmpleado(idUsuario)


# =================== GESTIÓN DE INTENTOS DE REPORTE (ADMIN) =================== #

@apis.route("/api/admin/intentos-reporte", methods=["GET"])
def obtener_intentos_reporte():
    """
    Endpoint para obtener todos los intentos de reporte (solo admin)
    """
    if not AuthController.is_logged_in():
        return jsonify({"error": "Debe estar logueado"}), 401
    
    # Verificar que sea administrador
    idUsuario = session.get('user_id')
    session_db = SessionLocal()
    try:
        usuario = session_db.query(Usuario).filter_by(idUsuario=idUsuario).first()
        if not usuario or not usuario.esAdministrador:
            return jsonify({"error": "Solo los administradores pueden acceder a esta información"}), 403
    finally:
        session_db.close()
    
    return EventosController.obtenerIntentosReporte()


@apis.route("/api/admin/intentos-reporte/<int:idIntentoReporte>", methods=["PUT"])
def actualizar_intento_reporte(idIntentoReporte):
    """
    Endpoint para actualizar un intento de reporte (observaciones, estado, etc.)
    """
    if not AuthController.is_logged_in():
        return jsonify({"error": "Debe estar logueado"}), 401
    
    # Verificar que sea administrador
    idUsuario = session.get('user_id')
    session_db = SessionLocal()
    try:
        usuario = session_db.query(Usuario).filter_by(idUsuario=idUsuario).first()
        if not usuario or not usuario.esAdministrador:
            return jsonify({"error": "Solo los administradores pueden modificar intentos de reporte"}), 403
    finally:
        session_db.close()
    
    data = request.get_json()
    return EventosController.actualizarIntentoReporte(idIntentoReporte, data)


@apis.route("/api/admin/intentos-reporte/<int:idIntentoReporte>/validar", methods=["POST"])
def validar_intento_reporte(idIntentoReporte):
    """
    Endpoint para validar un intento de reporte sin evento asociado
    """
    if not AuthController.is_logged_in():
        return jsonify({"error": "Debe estar logueado"}), 401
    
    # Verificar que sea administrador
    idUsuario = session.get('user_id')
    session_db = SessionLocal()
    try:
        usuario = session_db.query(Usuario).filter_by(idUsuario=idUsuario).first()
        if not usuario or not usuario.esAdministrador:
            return jsonify({"error": "Solo los administradores pueden validar intentos de reporte"}), 403
    finally:
        session_db.close()
    
    data = request.get_json() or {}
    observaciones = data.get("observaciones")
    return EventosController.validarIntentoReporte(idIntentoReporte, observaciones)


@apis.route("/api/admin/intentos-reporte/<int:idIntentoReporte>/rechazar", methods=["POST"])
def rechazar_intento_reporte(idIntentoReporte):
    """
    Endpoint para rechazar/descartar un intento de reporte
    """
    if not AuthController.is_logged_in():
        return jsonify({"error": "Debe estar logueado"}), 401
    
    # Verificar que sea administrador
    idUsuario = session.get('user_id')
    session_db = SessionLocal()
    try:
        usuario = session_db.query(Usuario).filter_by(idUsuario=idUsuario).first()
        if not usuario or not usuario.esAdministrador:
            return jsonify({"error": "Solo los administradores pueden rechazar intentos de reporte"}), 403
    finally:
        session_db.close()
    
    data = request.get_json() or {}
    observaciones = data.get("observaciones")
    return EventosController.rechazarIntentoReporte(idIntentoReporte, observaciones)


@apis.route("/api/admin/intentos-reporte/<int:idIntentoReporte>/verificar", methods=["POST"])
def verificar_intento_reporte(idIntentoReporte):
    """
    Endpoint para verificar un intento de reporte asociándolo a un evento
    """
    if not AuthController.is_logged_in():
        return jsonify({"error": "Debe estar logueado"}), 401
    
    # Verificar que sea administrador
    idUsuario = session.get('user_id')
    session_db = SessionLocal()
    try:
        usuario = session_db.query(Usuario).filter_by(idUsuario=idUsuario).first()
        if not usuario or not usuario.esAdministrador:
            return jsonify({"error": "Solo los administradores pueden verificar intentos de reporte"}), 403
    finally:
        session_db.close()
    
    data = request.get_json()
    if not data or "idEvento" not in data:
        return responseError("CAMPOS_OBLIGATORIOS", "Se requiere el campo 'idEvento'", 400)
    
    idEvento = data["idEvento"]
    observaciones = data.get("observaciones")
    return EventosController.verificarIntentoReporte(idIntentoReporte, idEvento, observaciones)


@apis.route("/api/admin/intentos-reporte/<int:idIntentoReporte>", methods=["DELETE"])
def eliminar_intento_reporte(idIntentoReporte):
    """
    Endpoint para eliminar un intento de reporte
    """
    if not AuthController.is_logged_in():
        return jsonify({"error": "Debe estar logueado"}), 401
    
    # Verificar que sea administrador
    idUsuario = session.get('user_id')
    session_db = SessionLocal()
    try:
        usuario = session_db.query(Usuario).filter_by(idUsuario=idUsuario).first()
        if not usuario or not usuario.esAdministrador:
            return jsonify({"error": "Solo los administradores pueden eliminar intentos de reporte"}), 403
    finally:
        session_db.close()
    
    return EventosController.eliminarIntentoReporte(idIntentoReporte)

@apis.route("/api/admin/limpiar-bd", methods=["DELETE"])
def limpiarBaseDatos():
    """
    Endpoint para limpiar completamente la base de datos.
    Elimina todos los datos: usuarios, áreas, eventos, resultados, etc.
    """
    if not AuthController.is_logged_in():
        return jsonify({"error": "Debe estar logueado para limpiar la base de datos"}), 401
    
    # Verificar que sea administrador
    idUsuario = session.get('user_id')
    session_db = SessionLocal()
    try:
        usuario = session_db.query(Usuario).filter_by(idUsuario=idUsuario).first()
        if not usuario or not usuario.esAdministrador:
            return jsonify({"error": "Solo los administradores pueden limpiar la base de datos"}), 403
    except Exception as e:
        session_db.close()
        return jsonify({"error": f"Error verificando permisos: {str(e)}"}), 500
    finally:
        session_db.close()
    
    # Limpiar la base de datos
    session_db = SessionLocal()
    try:
        # Eliminar en orden para respetar las foreign keys
        session_db.query(IntentoReporte).delete()
        session_db.query(UsuarioxEvento).delete()
        session_db.query(RegistroEvento).delete()
        session_db.query(Evento).delete()
        session_db.query(Usuario).delete()
        session_db.query(Area).delete()
        
        session_db.commit()
        log.info("Base de datos limpiada completamente")
        return jsonify({"mensaje": "Base de datos limpiada exitosamente"}), 200
        
    except Exception as e:
        session_db.rollback()
        log.error(f"Error limpiando base de datos: {str(e)}")
        return jsonify({"error": f"Error limpiando la base de datos: {str(e)}"}), 500
    finally:
        session_db.close()