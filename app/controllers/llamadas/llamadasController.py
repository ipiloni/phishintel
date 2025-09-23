from flask import Response, jsonify
from twilio.twiml.voice_response import Gather, VoiceResponse, Play

from app.backend.apis.elevenLabs import elevenLabs
from app.backend.apis.twilio import twilio
from app.backend.models.error import responseError
from app.controllers.aiController import AIController
from app.controllers.webScrappingController import WebScrappingController
from app.utils.config import get
from app.utils import conversacion
from app.utils.logger import log

password = get("LLAMAR_PASSWORD")

class LlamadasController:

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

            url = "https://veterinary-useful-attributes-dam.trycloudflare.com"  # localhost, ngrok o cuando se despliegue
            conversacion.urlAudioActual = f"{url}/api/audios/{idAudio}.mp3"

            log.info(f"La URL del audio actual es: {conversacion.urlAudioActual}")

            return twilio.llamar(destinatario, remitente, "https://veterinary-useful-attributes-dam.trycloudflare.com/api/twilio/accion")

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

            url = "https://veterinary-useful-attributes-dam.trycloudflare.com"  # localhost, ngrok o cuando se despliegue
            conversacion.urlAudioActual = f"{url}/api/audios/{idAudio}.mp3"

            log.info(f"URL audio actual: {conversacion.urlAudioActual}")

            response = VoiceResponse()

            response.play(conversacion.urlAudioActual)

            gather = Gather(
                input='speech',
                language="es-MX",
                action='https://veterinary-useful-attributes-dam.trycloudflare.com/api/twilio/respuesta',
                method='POST',
                speech_timeout='auto',
                timeout=3
            )

            response.append(gather)

            log.info(f"Lo que le mandamos a twilio es: {str(response)}")

            return Response(str(response), mimetype="application/xml")

        except Exception as e:
            log.error(f"Hubo un error en el procesamiento de la respuesta de la llamada: {str(e)}")
            return responseError("ERROR_AL_LLAMAR", f"Hubo un error al intentar ejecutar la llamada: {str(e)}", 500)

    @staticmethod
    def generarAccionesEnLlamada():
        log.info("Reproduciendo audio...")
        response = VoiceResponse()

        log.info(f"URL actual de audio: {conversacion.urlAudioActual}")

        response.play(conversacion.urlAudioActual)

        gather = Gather(
            input='speech',
            language="es-MX",
            action='https://veterinary-useful-attributes-dam.trycloudflare.com/api/twilio/respuesta',
            method='POST',
            speech_timeout='auto',
            timeout=3
        )

        response.append(gather)

        log.info(f"Lo que le mandamos a twilio es: {str(response)}")

        return Response(str(response), mimetype="application/xml")
