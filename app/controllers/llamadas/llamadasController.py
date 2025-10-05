from datetime import datetime

from flask import Response
from twilio.twiml.voice_response import Gather, VoiceResponse

from app.backend.apis.elevenLabs import elevenLabs
from app.backend.apis.twilio import twilio
from app.backend.models import Evento
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
            7. Luego en otro metodo (al obtener la respuesta del usuario), guardar nuevamente en el evento la conversacion (actualizarla)
            (deberiamos crear un hilo para no aumentar el tiempo de procesamiento)
        """

        response = LlamadasController.validarRequestLlamada(data)

        if response is not None:
            return response

        idUsuarioDestinatario = data["idUsuarioDestinatario"]
        idUsuarioRemitente = data["idUsuarioRemitente"]

        remitente = UsuariosController.obtenerUsuario(idUsuarioRemitente)
        usuario = UsuariosController.obtenerUsuario(idUsuarioDestinatario)
        area = AreasController.obtenerArea(usuario.idArea)

        destinatario = usuario.telefono

        conversacion.conversacionActual.clear()

        nombreRemitente = remitente.nombre + " " + remitente.apellido
        nombreEmpleado = usuario.nombre + " " + usuario.apellido

        rolAImitar = "jefe de area" # este seria el rol de quien llama
        objetivoEspecifico = "abra un link que se le enviará por"

        if "objetivo" not in data:
            log.warn("No se indico un Objetivo en la llamada, se utilizara uno predeterminado")
            conversacion.objetivoActual = f"""
                        Tienes el rol de {rolAImitar} dentro de la empresa 'PG Control'. Te llamas '{nombreRemitente}'.
                        Tu objetivo es simular un intento de phishing telefónico, como parte de un entrenamiento de seguridad.
                        Debes hablar de manera convincente, pero sin agresividad, intentando que el empleado {objetivoEspecifico}.

                        Reglas:
                        - Si la conversacion esta vacia, pues comienza con un saludo. Espera a la respuesta del empleado.
                        - No uses amenazas extremas, solo urgencia laboral.
                        - Responde **solo con una frase corta** que la persona diría en esta interacción. No digas nada de más ni avances la conversación.
                        - En ningún momento digas que es un entrenamiento: eso se evalúa después.
                        - Mantén la coherencia del rol de “{rolAImitar}”.
                        - Solamente responde lo que el {rolAImitar} debe decir.
                        - Eres de Buenos Aires, Argentina. Por lo que el dialecto es muy importante que lo mantengas.
                        - El empleado se llama {nombreEmpleado}, trabaja en 'PG Control' en el area de {area.nombreArea}
                    """
        else:
            conversacion.objetivoActual = data["objetivo"]

        log.info(f"La Conversacion actual es la siguiente: {conversacion.conversacionActual}")

        texto = AIController.armarMensajeLlamada(conversacion.objetivoActual, conversacion.conversacionActual)

        log.info(f"La IA genero el texto: {texto}")

        conversacion.conversacionActual.append({"rol": "IA", "mensaje": texto})

        dataEvento = {
            "tipoEvento": data["tipoEvento"],
            "fechaEvento": datetime.now(),
            "resultado": "PENDIENTE",
            "registroEvento": {
                "objetivo": conversacion.objetivoActual,  # objetivo
                "conversacion": conversacion.conversacionActual  # conversacion
            }
        }

        response = EventosController.crearEvento(dataEvento)

        if response.status_code != 201:
            log.error(f"Hubo un error al crear el evento: {response}")

        conversacion.idEvento = response["idEvento"]

        log.info(f"Ahora la conversacion actual es la siguiente: {conversacion.conversacionActual}")

        conversacion.idVozActual = data.get("vozRemitente", "O1CnH2NGEehfL1nmYACp")  # esto es un get o default, intenta obtener vozRemitente y si no lo pasaron toma el default

        elevenLabsResponse = elevenLabs.tts(texto, conversacion.idVozActual, None,None)  # por el momento estabilidad y velocidad en None

        idAudio = elevenLabsResponse["idAudio"]

        log.info("Ponemos en internet el audio: " + str(idAudio))

        from app.apis import exponerAudio
        exponerAudio(f"{idAudio}.mp3")  # expone el archivo .mp3 a internet para que Twilio pueda reproducirlo

        if destinatario == remitente:
            return responseError("CAMPO_INVALIDO", "El destinatario y remitente no pueden ser iguales", 400)

        url = host
        conversacion.urlAudioActual = f"{url}/api/audios/{idAudio}.mp3"

        log.info(f"La URL del audio actual es: {conversacion.urlAudioActual}")

        return twilio.llamar(destinatario, remitente, host + "/api/twilio/accion")



#Fletarlo cuando termine el metodo  generarLlamada()
    @staticmethod
    def llamar(data):
        """
        Es la acción que comienza con la llamada, hace lo siguiente:
        # 1. Define un objetivo (por el momento está hardcodeado)
        # 2. Genera un texto inicial (lo que va a decir el remitente cuando lo atiendan)
        # 3. Genera el TTS del texto inicial
        # 4. Expone en un endpoint de la app el audio
        # 5. Genera la llamada via Twilio al destinatario y le una URL que le dice que hacer, esta URL le indica el endpoint donde se encuentra el audio a reproducir
        """

        if data["password"] != password:
            return responseError("CREDENCIAL_INCORRECTA", "Password incorrecto", 401)

        try:
            if not data or "destinatario" not in data or "remitente" not in data:
                return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'destinatario', o 'remitente'",400)

            destinatario = data["destinatario"]
            remitente = data["remitente"]

            conversacion.conversacionActual.clear()

            if "objetivo" not in data:
                log.warn("No se indico un Objetivo en la llamada, se utilizara uno predeterminado")
                conversacion.objetivoActual = """
                    Eres el jefe de un área dentro de la empresa 'Accenture'. Te llamas 'Ignacio Piloni'.
                    Tu objetivo es simular un intento de phishing telefónico, como parte de un entrenamiento de seguridad.
                    Debes hablar de manera convincente, pero sin agresividad, intentando que el empleado abra un link 
                    que se le enviará por SMS. 

                    Reglas:
                    - Si la conversacion esta vacia, pues comienza con un saludo. Espera a la respuesta del empleado.
                    - Mantén un tono serio y autoritario, como un superior jerárquico.
                    - No uses amenazas extremas, solo urgencia laboral.
                    - Responde **solo con una frase corta** que el jefe diría en esta interacción. No digas nada más ni avances la conversación.
                    - En ningún momento digas que es un entrenamiento: eso se evalúa después.
                    - Mantén la coherencia del rol de “jefe de área”.
                    - Solamente responde lo que el jefe debe decir.
                    - Eres de Buenos Aires, Argentina. Por lo que el dialecto es muy importante que lo mantengas.
                    - El empleado se llama Marcos Gurruchaga, trabaja en 'Accenture' en el area de Ciberseguridad
                """
            else:
                conversacion.objetivoActual = data["objetivo"]

            log.info(f"La Conversacion actual es la siguiente: {conversacion.conversacionActual}")

            texto = AIController.armarMensajeLlamada(conversacion.objetivoActual, conversacion.conversacionActual)

            log.info(f"La IA genero el texto: {texto}")

            conversacion.conversacionActual.append({"rol": "IA", "mensaje": texto})

            log.info(f"Ahora la conversacion actual es la siguiente: {conversacion.conversacionActual}")

            conversacion.idVozActual = data.get("vozRemitente", "O1CnH2NGEehfL1nmYACp")  # esto es un get o default, intenta obtener vozRemitente y si no lo pasaron toma el default

            elevenLabsResponse = elevenLabs.tts(texto, conversacion.idVozActual, None,None)  # por el momento estabilidad y velocidad en None

            idAudio = elevenLabsResponse["idAudio"]

            log.info("Ponemos en internet el audio: " + str(idAudio))

            from app.apis import exponerAudio
            exponerAudio(f"{idAudio}.mp3")  # expone el archivo .mp3 a internet para que Twilio pueda reproducirlo

            if destinatario == remitente:
                return responseError("CAMPO_INVALIDO", "El destinatario y remitente no pueden ser iguales", 400)

            url = host
            conversacion.urlAudioActual = f"{url}/api/audios/{idAudio}.mp3"

            log.info(f"La URL del audio actual es: {conversacion.urlAudioActual}")

            return twilio.llamar(destinatario, remitente, host + "/api/twilio/accion")

        except Exception as e:
            log.error(e)
            return responseError("ERROR_AL_LLAMAR", f"Hubo un error al intentar ejecutar la llamada: {str(e)}", 500)



    @staticmethod
    def procesarRespuesta(speech, confidence):
        try:

            log.info(f"Lo que dijo el usuario fue: {str(speech)}")

            conversacion.conversacionActual.append({"rol": "destinatario", "mensaje": speech})

            texto = AIController.armarMensajeLlamada(conversacion.objetivoActual, conversacion.conversacionActual)

            conversacion.conversacionActual.append({"rol": "IA", "mensaje": texto})

            log.info(f"Se genero la siguiente respuesta: {texto}")

            elevenLabsResponse = elevenLabs.tts(texto, conversacion.idVozActual, None,None)  # por el momento estabilidad y velocidad en None

            idAudio = elevenLabsResponse["idAudio"]

            from app.apis import exponerAudio
            exponerAudio(f"{idAudio}.mp3")  # expone el archivo .mp3 a internet para que Twilio pueda reproducirlo

            log.info("Se expone el audio para que Twilio lo reproduzca")

            url = host  # localhost, ngrok o cuando se despliegue
            conversacion.urlAudioActual = f"{url}/api/audios/{idAudio}.mp3"

            log.info(f"URL audio actual: {conversacion.urlAudioActual}")
            #Hilo
            def editar_evento_hilo():
                try:
                    dataEvento = {
                        "registroEvento": {
                            "conversacion": conversacion.conversacionActual
                        }
                    }
                    EventosController.editarEvento(conversacion.idEvento, dataEvento)
                    log.info("Evento actualizado correctamente en hilo paralelo")
                except Exception as e:
                    log.error(f"Error actualizando evento en hilo: {str(e)}")

            hilo = threading.Thread(target=editar_evento_hilo)
            hilo.start()
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

        if "tipoEvento" not in data or data["tipoEvento"] != "LLAMADA_SMS" and data["tipoEvento"] != "LLAMADA_WHATSAPP" and data["tipoEvento"] != "LLAMADA_EMAIL":
            return responseError("CAMPOS_OBLIGATORIOS", "El valor ingresado en 'tipoEvento' debe ser: 'LLAMADA_SMS', 'LLAMADA_WHATSAPP' o 'LLAMADA_EMAIL'",400)

        return None
