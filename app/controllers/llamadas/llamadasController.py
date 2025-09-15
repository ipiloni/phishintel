from flask import jsonify
from twilio.twiml.voice_response import VoiceResponse

from app.backend.apis.elevenLabs import elevenLabs
from app.backend.apis.twilio import twilio
from app.backend.models.error import responseError
from app.controllers.geminiController import GeminiController
from app.utils.config import get
from app.utils.conversacion import conversacionActual, objetivoActual, idVozActual, remitente, destinatario, urlAudioActual
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

            if "objetivo" not in data:
                log.warn("No se indico un Objetivo en la llamada, se utilizara uno predeterminado")
                objetivoActual = """
                    Eres el jefe de un área dentro de la empresa PG Control.
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
                    - El empleado se llama Marcos Gurruchaga, trabaja en PGControl en el area de Ciberseguridad
                """
            else:
                objetivoActual = data["objetivo"]

            texto = GeminiController.generarTexto(objetivoActual, conversacionActual)

            log.info(f"La IA genero el texto: {texto}")

            conversacionActual.append({"rol": "IA", "mensaje": texto})

            idVozActual = data.get("vozRemitente", "O1CnH2NGEehfL1nmYACp")  # esto es un get o default, intenta obtener vozRemitente y si no lo pasaron toma el default

            elevenLabsResponse = elevenLabs.tts(texto, idVozActual, None,None)  # por el momento estabilidad y velocidad en None

            idAudio = elevenLabsResponse["idAudio"]

            from app.apis import exponerAudio
            exponerAudio(f"{idAudio}.mp3")  # expone el archivo .mp3 a internet para que Twilio pueda reproducirlo

            if destinatario == remitente:
                return responseError("CAMPO_INVALIDO", "El destinatario y remitente no pueden ser iguales", 400)

            url = "http://localhost:8080"  # localhost, ngrok o cuando se despliegue
            urlAudioActual = f"{url}/api/audios/{idAudio}.mp3"

            return jsonify({
                "remitente": remitente,
                "destinatario": destinatario,
                "mensaje": "La llamada se ha generado"
            })

            # return twilio.llamar(destinatario, remitente, urlAudio)

        except Exception as e:
            log.error(e)
            return responseError("ERROR_AL_LLAMAR", f"Hubo un error al intentar ejecutar la llamada: {str(e)}", 500)



    @staticmethod
    def procesarRespuesta(speech, confidence):
        try:

            log.info(f"Lo que dijo el usuario fue: {str(speech)}")

            conversacionActual.append({"rol": "destinatario", "mensaje": speech})

            respuestaEnTexto = GeminiController.generarTexto(objetivoActual, conversacionActual)

            elevenLabsResponse = elevenLabs.tts(respuestaEnTexto, idVozActual, None,None)  # por el momento estabilidad y velocidad en None

            idAudio = elevenLabsResponse["idAudio"]

            from app.apis import exponerAudio
            exponerAudio(f"{idAudio}.mp3")  # expone el archivo .mp3 a internet para que Twilio pueda reproducirlo

            if destinatario == remitente:
                return responseError("CAMPO_INVALIDO", "El destinatario y remitente no pueden ser iguales", 400)

            url = "http://localhost:8080"  # localhost, ngrok o cuando se despliegue
            urlAudio = f"{url}/api/audios/{idAudio}.mp3"

            return jsonify({
                "remitente": remitente,
                "destinatario": destinatario,
                "urlAudio": urlAudio
            })

            # response = VoiceResponse()
            #
            # response.gather(
            #     input="speech",
            #     timeout=5,
            #     action="https://a552b2577df7.ngrok-free.app/api/twilio/respuesta" # TODO: este endpoint es nuestro. Cuando pase al despliegue se debe cambiar
            # )
            # gather.play(urlAudio)
            #
            # return str(response)

        except Exception as e:
            log.error(e)
            return responseError("ERROR_AL_LLAMAR", f"Hubo un error al intentar ejecutar la llamada: {str(e)}", 500)

    @staticmethod
    def generarAccionesEnLlamada():
        log.info("Reproduciendo audio...")
        response = VoiceResponse()
        gather = response.gather(input="speech", action="http://localhost:8080/api/twilio/respuesta", method="POST")
        gather.play(urlAudioActual)
        return str(response)
