import json
import random
import time
import threading
from datetime import datetime

from flask import jsonify

from app.backend.models.error import responseError
from app.backend.models.tipoEvento import TipoEvento
from app.controllers.abm.areasController import AreasController
from app.controllers.abm.eventosController import EventosController
from app.controllers.abm.usuariosController import UsuariosController
from app.controllers.aiController import AIController
from app.controllers.emails.emailController import EmailController
from app.controllers.mensajes.msjController import MsjController
from app.controllers.resultadoEventoController import ResultadoEventoController
from app.utils import conversacion
from app.utils.logger import log

# Conversación hardcodeada con flujo lógico
# Secuencia fija de mensajes que sigue un flujo realista
CONVERSACION_FLUJO = [
    {"rol": "IA", "mensaje": "Hola, buenos días. ¿Habla con usted?"},
    {"rol": "destinatario", "mensaje": "Sí, habla conmigo. ¿Quién es?"},
    {"rol": "IA", "mensaje": "Hola, soy del área de sistemas de la empresa. Te llamo porque necesitamos que actualices algunos datos importantes en el sistema."},
    {"rol": "destinatario", "mensaje": "Ah, claro. ¿Qué datos necesitan actualizar exactamente?"},
    {"rol": "IA", "mensaje": "Necesitamos que actualices tu información de contacto y tus credenciales de acceso. Es importante para mantener la seguridad del sistema."},
    {"rol": "destinatario", "mensaje": "Entendido. ¿Cómo puedo hacerlo?"},
    {"rol": "IA", "mensaje": "Te voy a enviar un enlace por correo para que puedas hacerlo de forma segura. Por favor, revisa tu correo y completa el formulario lo antes posible."},
    {"rol": "destinatario", "mensaje": "Perfecto, estaré atento al mensaje y lo haré en cuanto lo reciba."},
    {"rol": "IA", "mensaje": "Excelente. Gracias por tu colaboración. Es urgente que lo completes hoy mismo. Que tengas un buen día."},
    {"rol": "destinatario", "mensaje": "De acuerdo, lo haré. Gracias por avisar. Hasta luego."}
]

# Estados de la llamada simulada
ESTADO_SIMULADO = {
    "sid": "",
    "status": "queued",
    "mensaje_actual": 0
}


class LlamadaControllerMentira:

    @staticmethod
    def generarLlamadaSimulada(data):
        """
        Genera una llamada simulada con mensajes predefinidos.
        Recibe los mismos parámetros que generarLlamada pero simula todo el proceso.
        """
        # Validar request
        response = LlamadaControllerMentira.validarRequestLlamada(data)
        if response is not None:
            return response

        idUsuarioDestinatario = data["idUsuarioDestinatario"]
        idUsuarioRemitente = data["idUsuarioRemitente"]
        eventoDesencadenador = data.get("eventoDesencadenador", "Correo")

        # Reinicio y seteo variables globales de la conversacion
        conversacion.hilo = False
        conversacion.destinatario = idUsuarioDestinatario
        conversacion.remitente = idUsuarioRemitente
        conversacion.objetivoEspecifico = data.get("objetivoEspecifico", "Abra un link para actualizar sus datos que se le enviara por")
        conversacion.eventoDesencadenador = eventoDesencadenador

        # Obtengo usuarios de la base
        remitente, statusRemitente = UsuariosController.obtenerUsuario(idUsuarioRemitente)
        usuario, statusUsuario = UsuariosController.obtenerUsuario(idUsuarioDestinatario)

        # Se validan las respuestas de la base
        if statusRemitente != 200:
            log.warning("No se encontro un idUsuarioRemitente existente")
            return responseError("USUARIO_INEXISTENTE", "No se encontro un idUsuarioRemitente existente", 400)

        if statusUsuario != 200:
            log.warning("No se encontro un idUsuarioDestinatario existente")
            return responseError("USUARIO_INEXISTENTE", "No se encontro un idUsuarioDestinatario existente", 400)

        # Obtengo los valores de los usuarios consultados
        remitente = remitente.get_json()
        usuario = usuario.get_json()

        # Se obtiene el area del usuario
        area, statusArea = AreasController.obtenerArea(usuario["idArea"])
        if statusArea != 200:
            log.warning("El usuario no pertenece a ningun Area particular")
            return responseError("AREA_INEXISTENTE", f"El usuario de id: {idUsuarioDestinatario} debe pertenecer a un area para generar la llamada", 400)

        area = area.get_json()

        # Elimino de la variable global la conversacion anterior
        conversacion.conversacionActual.clear()

        nombreRemitente = remitente["nombre"] + " " + remitente["apellido"]
        nombreEmpleado = usuario["nombre"] + " " + usuario["apellido"]

        rolAImitar = data.get("rolAImitar", "Jefe")
        objetivoEspecifico = data.get("objetivoEspecifico", "Abra un link para actualizar sus datos que se le enviara por")

        conversacion.objetivoActual = f"""
            Simulación de llamada de phishing.
            Rol: {rolAImitar}
            Remitente: {nombreRemitente}
            Destinatario: {nombreEmpleado}
            Objetivo: {objetivoEspecifico} {eventoDesencadenador}
        """

        # Crear evento en la base de datos
        dataEvento = {
            "tipoEvento": "LLAMADA",
            "registroEvento": {
                "objetivo": " ".join(conversacion.objetivoActual.split()).strip(),
            }
        }

        log.info(f"{dataEvento}")

        resp = EventosController.crearEvento(dataEvento)

        if isinstance(resp, tuple):
            responseEvento, statusResponse = resp
        else:
            responseEvento = resp
            statusResponse = resp.status_code

        if statusResponse != 201:
            log.error(f"Hubo un error al crear el evento: {responseEvento.get_data(as_text=True)}")
            return responseEvento, statusResponse

        data_evento = responseEvento.get_json()
        conversacion.idEvento = data_evento["idEvento"]

        log.info("Evento creado correctamente, creamos el Usuario por Evento")

        responseUsuarioEvento, statusUsuarioEvento = EventosController.asociarUsuarioEvento(
            conversacion.idEvento, idUsuarioDestinatario, "PENDIENTE"
        )
        responseUsuarioEvento = responseUsuarioEvento.get_json()

        if statusUsuarioEvento != 200:
            log.error(f"Hubo un error al asociar el usuario al evento: {responseUsuarioEvento}")
            return responseUsuarioEvento, statusUsuarioEvento

        # Generar ID de conversación simulado con prefijo SIM_
        sid_simulado = f"SIM_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
        conversacion.idConversacion = sid_simulado

        # Inicializar estado de la llamada simulada
        ESTADO_SIMULADO["sid"] = sid_simulado
        ESTADO_SIMULADO["status"] = "queued"
        ESTADO_SIMULADO["mensaje_actual"] = 0

        # Iniciar el hilo que simula la llamada
        hilo = threading.Thread(target=LlamadaControllerMentira.simularProgresoLlamada)
        hilo.daemon = True
        hilo.start()

        log.info(f"Llamada simulada iniciada con SID: {sid_simulado}")

        return jsonify({
            'sid': sid_simulado,
            'status': 'queued'
        }), 201

    @staticmethod
    def simularProgresoLlamada():
        """
        Simula el progreso de una llamada agregando mensajes y cambiando estados.
        """
        import time

        # Esperar un poco antes de iniciar
        time.sleep(1)

        # Cambiar estado a initiated
        ESTADO_SIMULADO["status"] = "initiated"
        time.sleep(2)

        # Cambiar estado a ringing
        ESTADO_SIMULADO["status"] = "ringing"
        time.sleep(2)

        # Cambiar estado a in-progress
        ESTADO_SIMULADO["status"] = "in-progress"

        # Agregar mensajes siguiendo el flujo lógico de la conversación hardcodeada
        for mensaje_obj in CONVERSACION_FLUJO:
            # Agregar el mensaje a la conversación
            conversacion.conversacionActual.append(mensaje_obj)
            ESTADO_SIMULADO["mensaje_actual"] += 1

            # Actualizar evento en paralelo
            def actualizarEvento():
                try:
                    dataEvento = {
                        "registroEvento": {
                            "conversacion": json.dumps(conversacion.conversacionActual)
                        }
                    }
                    statusEvento = EventosController.editarEvento(conversacion.idEvento, dataEvento)
                    if statusEvento != 200:
                        log.error("No se pudo actualizar el evento en hilo paralelo")
                    else:
                        log.info("Evento actualizado correctamente en hilo paralelo")
                except Exception as e:
                    log.error(f"Error actualizando evento en hilo: {str(e)}")

            hilo_actualizacion = threading.Thread(target=actualizarEvento)
            hilo_actualizacion.start()

            # Esperar entre mensajes (3-5 segundos)
            time.sleep(random.uniform(3, 5))

        # Después de todos los mensajes, cambiar estado a completed
        ESTADO_SIMULADO["status"] = "completed"

        # Ejecutar lógica de envío de mail/mensaje (similar a analizarLlamada)
        log.info("Llamada simulada completada, generando evento posterior...")
        LlamadaControllerMentira.generarEventoPosterior()

    @staticmethod
    def generarEventoPosterior():
        """
        Genera el evento posterior (mail o mensaje) después de completar la llamada simulada.
        """
        try:
            # Marcar como falla (objetivo cumplido en simulación)
            ResultadoEventoController.sumarFalla(conversacion.destinatario, conversacion.idEvento)

            if conversacion.eventoDesencadenador.lower() == "correo":
                log.info("El evento desencadenador es un correo, generando email...")

                # Generar email con dificultad difícil y mensaje genérico
                contexto = "Se pedirá actualización urgente de datos con enlace a caisteDatos.html. Empresa: PG Control. Sin placeholders. No incluyas enlaces; indica que el enlace se adjuntará a continuación."
                data = {
                    "contexto": contexto,
                    "nivel": 3,
                    "formato": "texto"
                }
                respuesta = AIController.armarEmail(data)

                # armarEmail devuelve (texto_json, 201) o responseError (Response)
                if isinstance(respuesta, tuple):
                    respuesta_texto, status = respuesta
                    if status != 201:
                        log.error(f"La IA no pudo armar el email: {respuesta_texto}")
                        return
                else:
                    # Es un Response de error
                    if hasattr(respuesta, 'status_code') and respuesta.status_code != 201:
                        log.error(f"La IA no pudo armar el email")
                        return
                    respuesta_texto = respuesta.get_data(as_text=True) if hasattr(respuesta, 'get_data') else str(respuesta)

                try:
                    data_email = json.loads(respuesta_texto)
                except (json.JSONDecodeError, TypeError) as e:
                    log.error(f"El texto devuelto no es JSON válido: {respuesta_texto}, error: {str(e)}")
                    return

                dataMail = {
                    "proveedor": "twilio",
                    "idUsuarioDestinatario": conversacion.destinatario,
                    "idUsuarioRemitente": conversacion.remitente,
                    "asunto": data_email["asunto"],
                    "cuerpo": data_email["cuerpo"],
                    "dificultad": "dificil"
                }

                EmailController.enviarMailPorID(dataMail)

            else:
                log.info(f"El evento desencadenador es un mensaje, generando mensaje...")

                # Generar mensaje según el objetivo específico
                if conversacion.objetivoEspecifico == "Abra un link que se le enviara por":
                    dificultad = "facil"
                    contexto = "Genera un mensaje de phishing formal para empleados de PG Control, contexto variable, sin marcadores como [Nombre de la empresa], no incluyas ningún enlace; indica que el enlace se adjuntará a continuación."
                elif conversacion.objetivoEspecifico == "Abra un link para ingresar sus credenciales que se le enviara por":
                    dificultad = "medio"
                    contexto = "Se pedirá login en un formulario (como caisteLogin.html) y credenciales. Empresa: PG Control. Sin placeholders. No incluyas enlaces; indica que el enlace se adjuntará a continuación."
                else:
                    dificultad = "dificil"
                    contexto = "Se pedirá actualización urgente de datos con enlace a caisteDatos.html. Empresa: PG Control. Sin placeholders. No incluyas enlaces; indica que el enlace se adjuntará a continuación."

                datamsj2 = {
                    "contexto": contexto,
                    "nivel": dificultad
                }
                respuesta = AIController.armarMensaje(datamsj2)

                # armarMensaje devuelve ({"mensaje": texto}, 201) o responseError (Response)
                if isinstance(respuesta, tuple):
                    respuesta_dict, status = respuesta
                    if status != 201:
                        log.error(f"La IA no pudo armar el mensaje: {respuesta_dict}")
                        return
                    mensaje_texto = respuesta_dict.get("mensaje", "")
                else:
                    # Es un Response de error
                    if hasattr(respuesta, 'status_code') and respuesta.status_code != 201:
                        log.error(f"La IA no pudo armar el mensaje")
                        return
                    # Intentar obtener JSON del error
                    try:
                        respuesta_dict = respuesta.get_json() if hasattr(respuesta, 'get_json') else {}
                        mensaje_texto = respuesta_dict.get("mensaje", "")
                    except:
                        log.error(f"Error procesando respuesta de armarMensaje")
                        return

                datamsj = {
                    "medio": conversacion.eventoDesencadenador.lower(),
                    "idUsuario": conversacion.destinatario,
                    "mensaje": mensaje_texto,
                    "dificultad": dificultad
                }
                MsjController.enviarMensajePorID(datamsj)

        except Exception as e:
            log.error(f"Error generando evento posterior: {str(e)}")

    @staticmethod
    def obtenerEstadoLlamadaSimulada():
        """
        Obtiene el estado actual de la llamada simulada.
        """
        if ESTADO_SIMULADO["sid"] == "":
            return None

        return {
            "sid": ESTADO_SIMULADO["sid"],
            "status": ESTADO_SIMULADO["status"]
        }

    @staticmethod
    def validarRequestLlamada(data):
        """
        Valida los datos del request para generar una llamada simulada.
        """
        password = "phishintel2025"  # Mismo password que el real

        if not data or "password" not in data:
            return responseError("CREDENCIAL_INCORRECTA", "Credencial incorrecta", 401)

        if data["password"] != password:
            return responseError("CREDENCIAL_INCORRECTA", "Credencial incorrecta", 401)

        if "idUsuarioDestinatario" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'idUsuarioDestinatario'", 400)

        if "idUsuarioRemitente" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'idUsuarioRemitente'", 400)

        return None

