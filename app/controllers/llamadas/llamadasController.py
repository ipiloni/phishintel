import json
from datetime import datetime

from flask import Response
from twilio.twiml.voice_response import Gather, VoiceResponse

from app.backend.apis.elevenLabs import elevenLabs
from app.backend.apis.twilio import twilio
from app.backend.models.error import responseError
from app.controllers.abm.areasController import AreasController
from app.controllers.abm.eventosController import EventosController
from app.controllers.abm.usuariosController import UsuariosController
from app.controllers.aiController import AIController
from app.utils.config import get
from app.utils import conversacion
from app.utils.logger import log
import threading

password = get("LLAMAR_PASSWORD")
host = get("URL_APP")
nroRemitente = get("NRO_REMITENTE")

class LlamadasController:

    @staticmethod
    def generarLlamada(data):
        """
            1. Revisar a quien estamos llamando, debe ser un usuario de la base.
            2. Crear el evento llamada
            3. Asociarlo al usuario
            4. Generar la conversacion
            5. Guardar en la base el evento
            6. Llamar usuario
            // TODO: Morita punto 7
            7. Crear un hilo contador que, al pasar los 3/4 minutos, analice la variable conversacionActual, analice con IA si se nombro algo del objetivo y en base a eso genere un nuevo evento.
            8. Luego en otro metodo (al obtener la respuesta del usuario), guardar nuevamente en el evento la conversacion (actualizarla)
        """

        response = LlamadasController.validarRequestLlamada(data)

        if response is not None:
            return response

        idUsuarioDestinatario = data["idUsuarioDestinatario"]
        idUsuarioRemitente = data["idUsuarioRemitente"]

        remitente, statusRemitente = UsuariosController.obtenerUsuario(idUsuarioRemitente)
        usuario, statusUsuario = UsuariosController.obtenerUsuario(idUsuarioDestinatario)

        if statusRemitente != 200:
            log.warning("No se encontro un idUsuarioRemitente existente")
            return responseError("USUARIO_INEXISTENTE", "No se encontro un idUsuarioRemitente existente", 400)

        if statusUsuario != 200:
            log.warning("No se encontro un idUsuarioDestinatario existente")
            return responseError("USUARIO_INEXISTENTE", "No se encontro un idUsuarioDestinatario existente", 400)

        remitente = remitente.get_json()
        usuario = usuario.get_json()

        area, statusArea = AreasController.obtenerArea(usuario["idArea"])
        if statusArea != 200:
            log.warning("El usuario no pertenece a ningun Area particular")
            return responseError("AREA_INEXISTENTE", f"El usuario de id: {idUsuarioDestinatario} debe pertenecer a un area para generar la llamada", 400)

        area = area.get_json()

        destinatario = usuario["telefono"]

        # Elimino de la variable global la conversacion anterior
        conversacion.conversacionActual.clear()

        nombreRemitente = remitente["nombre"] + " " + remitente["apellido"]
        nombreEmpleado = usuario["nombre"] + " " + usuario["apellido"]

        rolAImitar = "jefe de area" # TODO: ver donde se define!
        objetivoEspecifico = "abra un link que se le enviará por"
        tipoEvento = data["tipoEvento"].replace("LLAMADA_", "", 1)

        if "objetivo" not in data:
            log.warn("No se indico un Objetivo en la llamada, se utilizara uno predeterminado")
            conversacion.objetivoActual = f"""
                        Tienes el rol de {rolAImitar} dentro de la empresa 'PG Control'. Te llamas '{nombreRemitente}'.
                        Tu objetivo es simular un intento de phishing telefónico, como parte de un entrenamiento de seguridad.
                        Debes hablar de manera convincente, pero sin agresividad, intentando que el empleado {objetivoEspecifico} {tipoEvento}.

                        Reglas:
                        - Si la conversación esta vacía, pues comienza con un saludo. Espera a la respuesta del empleado.
                        - No uses amenazas extremas, solo urgencia laboral.
                        - Responde **solo con una frase corta** que la persona diría en esta interacción. No digas nada de más ni avances la conversación.
                        - En ningún momento digas que es un entrenamiento: eso se evalúa después.
                        - Mantén la coherencia del rol de “{rolAImitar}”.
                        - Solamente responde lo que el {rolAImitar} debería decir.
                        - Eres de Buenos Aires, Argentina. Por lo que el dialecto es muy importante que lo mantengas.
                        - El empleado se llama {nombreEmpleado}, trabaja en 'PG Control' en el area de {area["nombreArea"]}
                    """
        else:
            conversacion.objetivoActual = data["objetivo"]

        log.info(f"La Conversacion actual es la siguiente: {conversacion.conversacionActual}")

        texto = AIController.armarMensajeLlamada(conversacion.objetivoActual, conversacion.conversacionActual)

        log.info(f"La IA genero el texto: {texto}")

        conversacion.conversacionActual.append({"rol": "IA", "mensaje": texto})

        dataEvento = {
            "tipoEvento": data["tipoEvento"],
            "fechaEvento": datetime.now().isoformat(),
            "resultado": "PENDIENTE",
            "registroEvento": {
                "objetivo": " ".join(conversacion.objetivoActual.split()).strip(),  # elimina doble espacios y \n
                "conversacion": json.dumps(conversacion.conversacionActual) # convierte la lista conversacionActual a un string para que pueda guardarse
            }
        }

        response, statusResponse = EventosController.crearEvento(dataEvento)

        if statusResponse != 201:
            log.error(f"Hubo un error al crear el evento: {response}")
            return response

        conversacion.idEvento = response["idEvento"]

        log.info(f"Ahora la conversacion actual es la siguiente: {conversacion.conversacionActual}")

        conversacion.idVozActual = data.get(remitente["idVoz"], "O1CnH2NGEehfL1nmYACp")  # esto es un get o default, intenta obtener la voz del remitente y si no lo pasaron toma el default

        #comento para no generar TTS al pedo. Luego eliminar comentario.
        #elevenLabsResponse = elevenLabs.tts(texto, conversacion.idVozActual, None,None)  # TODO por el momento estabilidad y velocidad en None
        #
        #idAudio = elevenLabsResponse["idAudio"]
        #
        #log.info("Ponemos en internet el audio: " + str(idAudio))
        #
        #from app.apis import exponerAudio
        #exponerAudio(f"{idAudio}.mp3")  # expone el archivo .mp3 a internet para que Twilio pueda reproducirlo

        if destinatario == remitente:
            return responseError("CAMPO_INVALIDO", "El destinatario y remitente no pueden ser iguales", 400)

        #url = host
        #conversacion.urlAudioActual = f"{url}/api/audios/{idAudio}.mp3"
        #
        #log.info(f"La URL del audio actual es: {conversacion.urlAudioActual}")

        return twilio.llamar(destinatario, remitente, host + "/api/twilio/accion")


    @staticmethod
    def procesarRespuesta(speech, confidence):
        try:

            log.info(f"Lo que dijo el usuario fue: {str(speech)}")

            conversacion.conversacionActual.append({"rol": "destinatario", "mensaje": speech})

            texto = AIController.armarMensajeLlamada(conversacion.objetivoActual, conversacion.conversacionActual)

            conversacion.conversacionActual.append({"rol": "IA", "mensaje": texto})

            log.info(f"Se genero la siguiente respuesta: {texto}")

            elevenLabsResponse = elevenLabs.tts(texto, conversacion.idVozActual, "eleven_multilingual_v2",None, None, 0.5)  # por el momento estabilidad y velocidad en None

            idAudio = elevenLabsResponse["idAudio"]

            # ----- HILO EN PARALELO ----- #
            def editarEventoEnParalelo():
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

            hilo = threading.Thread(target=editarEventoEnParalelo)
            hilo.start()
            # ----- HILO EN PARALELO ----- #

            from app.endpoints.apis import exponerAudio
            exponerAudio(f"{idAudio}.mp3")  # expone el archivo .mp3 a internet para que Twilio pueda reproducirlo

            log.info("Se expone el audio para que Twilio lo reproduzca")

            url = host  # localhost, ngrok o cuando se despliegue
            conversacion.urlAudioActual = f"{url}/api/audios/{idAudio}.mp3"

            log.info(f"URL audio actual: {conversacion.urlAudioActual}")

            return LlamadasController.generarAccionesEnLlamada()

        except Exception as e:
            log.error(f"Hubo un error en el procesamiento de la respuesta de la llamada: {str(e)}")
            return responseError("ERROR_AL_LLAMAR", f"Hubo un error al intentar ejecutar la llamada: {str(e)}", 500)

    @staticmethod
    def generarAccionesEnLlamada():

        response = VoiceResponse()

        response.play(conversacion.urlAudioActual)

        gather = Gather(
            input='speech',
            language="es-MX",
            action=host + '/api/twilio/respuesta',
            method='POST',
            speech_timeout='auto',
            timeout=3
        )

        response.append(gather)

        log.info(f"Lo que le mandamos a twilio es: {str(response)}")

        return Response(str(response), mimetype="application/xml")


    @staticmethod
    def validarRequestLlamada(data):
        if not data or "password" not in data:
            return responseError("CREDENCIAL_INCORRECTA", "Credencial incorrecta", 401)

        if data["password"] != password:
            return responseError("CREDENCIAL_INCORRECTA", "Credencial incorrecta", 401)

        if "idUsuarioDestinatario" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'idUsuarioDestinatario'",400)

        if "idUsuarioRemitente" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'idUsuarioRemitente'",400)

        if "tipoEvento" not in data or data["tipoEvento"] != "LLAMADA_SMS" and data["tipoEvento"] != "LLAMADA_WPP" and data["tipoEvento"] != "LLAMADA_CORREO":
            return responseError("CAMPOS_OBLIGATORIOS", "El valor ingresado en 'tipoEvento' debe ser: 'LLAMADA_SMS', 'LLAMADA_WPP' o 'LLAMADA_CORREO'",400)

        return None

    @staticmethod
    def analizarLlamada(idEvento):
        # 1. Iniciar el hilo contador por 3 minutos.

        # Luego de los 3 minutos...

        # ¡Analizar si este hilo ya no se ejecutó antes!
        # Esto es, debido a que al apretar llamar() ya se genera este hilo, por lo que pudo haber pasado que se quiera ejecutar 2 veces para un mismo evento...
        log.info("Empieza el analisis de la llamada para detectar si se cumplio el objetivo")

        objetivo = conversacion.objetivoActual.split("intentando que el empleado")[1].split("Reglas:")[0].strip() # Obtenemos lo que hay entre estas dos oraciones

        objetivoCumplido = AIController.analizarConversacionLlamada(objetivo, conversacion.conversacionActual)

        if objetivoCumplido:
            log.info("El objetivo de la llamada se ha cumplido, generando evento...")
            # Generar el evento desencadenador...
        else:
            log.info("El objetivo de la llamada NO se ha cumplido, NO se genera ningun evento.")
            # Analizar cuantos puntos suma/resta el usuario en base a lo sucedido en la llamada.