from flask import Response, jsonify
from twilio.twiml.voice_response import VoiceResponse

from app.apis import enviarAudio
from app.backend.apis.ai import gemini
from app.backend.apis.twilio import twilio
from app.backend.models.error import responseError
from app.controllers.llamadas.elevenLabsController import ElevenLabsController
from app.utils.logger import log

class LlamadasController:

    # TODO: Esto deberemos hacerlo cuando podamos llamar!!!

    @staticmethod
    def llamar(data):
        if not data or "destinatario" not in data or "remitente" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'destinatario', o 'remitente'", 400)

        destinatario = data["destinatario"]
        remitente = data["remitente"]

        if destinatario == remitente:
            return responseError("CAMPO_INVALIDO", "El destinatario y remitente no pueden ser iguales", 400)

        return twilio.llamar(destinatario, remitente)

    # @staticmethod
    # def generarLlamada(idDestinatario, idRemitente, objetivo):
    #
    # # 1. obtener destinatario y remitente, en caso de que no existan o que el numero de telefono
    # # del destinatario no este cargado en la base, se tira un error 404.
    #
    # # 2. Armar el prompt en la IA (dolor de huevos/ovarios)
    #


    # @staticmethod
    # def generarEndpointAudio(ubicacionAudio):
    #
    #     @app.route("/audio_endpoint", methods=["GET", "POST"])
    #     def audio_endpoint():
    #         response = VoiceResponse()
    #         # Twilio requiere que el audio esté accesible públicamente por URL
    #         response.play(ubicacionAudio)
    #         return Response(str(response), mimetype="text/xml")
    #
    #     # Devuelve la URL absoluta del endpoint (para pasársela al create call)
    #     return url_for("audio_endpoint", _external=True)

    # @staticmethod
    # def generarRespuesta(data):
    #     if not data or "conversacion" not in data or "objetivo" not in data:

    @staticmethod
    def procesarRespuesta(speech, confidence):
        # if confidence es bajo => quiere decir que la transcripcion no fue buena (no se entendio), podemos pedirle al usuario que repita lo que dijo.
        # speech ya es el texto de lo que dijo, esta transcripto

        log.info(f"Lo que dijo el usuario fue: {str(speech)}")

        # la conversacion deberia estar en memoria para no tardar tiempo. Como va a ser siempre 1 a la vez y no mas, podemos hacerlo
        conversacion = []

        conversacion.append(speech)
        # 3. generar una respuesta
        respuestaEnTexto = gemini.generarRespuesta(conversacion)

        # 3.1. armar el audio
        data = jsonify({
            "texto": respuestaEnTexto,
            "idVoz": "O1CnH2NGEehfL1nmYACp", # TODO: obtenerlo de la conversacion, del remitente!
            "estabilidad": 0.5,
            "velocidad": "normal"
        })
        audio = ElevenLabsController.generarTTS(data)
        
        # 3.2. exponer audio en internet
        urlAudio = enviarAudio(audio)

        # 4. enviar a twilio un audio con la respuesta
        response = VoiceResponse()
        response.play(urlAudio)

        response.gather(
            input="speech",
            timeout=5,
            action="https://a552b2577df7.ngrok-free.app/api/twilio/respuesta" # TODO: este endpoint es nuestro. Cuando pase al despliegue se debe cambiar 
        )
        
        return Response(str(response), mimetype="text/xml")
