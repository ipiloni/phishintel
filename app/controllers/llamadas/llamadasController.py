from flask import Response, jsonify
from twilio.twiml.voice_response import VoiceResponse

from app.backend.apis.twilio import twilio
from app.backend.models.error import responseError
from app.controllers.llamadas.elevenLabsController import ElevenLabsController
from app.utils.logger import log

class LlamadasController:

    @staticmethod
    def llamar(data):
        if not data or "destinatario" not in data or "remitente" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'destinatario', o 'remitente'", 400)

        objetivo = """
            Eres el jefe de un área dentro de la empresa PG Control.
            Tu objetivo es simular un intento de phishing telefónico, como parte de un entrenamiento de seguridad.
            Debes hablar de manera convincente, pero sin agresividad, intentando que el empleado abra un link 
            que se le enviará por SMS. 
    
            Reglas:
            - Mantén un tono serio y autoritario, como un superior jerárquico.
            - No uses amenazas extremas, solo urgencia laboral.
            - Habla en frases cortas, naturales, como en una llamada real.
            - En ningún momento digas que es un entrenamiento: eso se evalúa después.
            - Mantén la coherencia del rol de “jefe de área”.
            - Solamente responde lo que el jefe debe decir.
        """

        destinatario = data["destinatario"]
        remitente = data["remitente"]
        # objetivo = data["objetivo"]

        # url_audio = obtenerUrlAudio(objetivo);
        url_audio = None

        if destinatario == remitente:
            return responseError("CAMPO_INVALIDO", "El destinatario y remitente no pueden ser iguales", 400)

        return twilio.llamar(destinatario, remitente, url_audio)


    @staticmethod
    def procesarRespuesta(speech, confidence):
        # if confidence es bajo => quiere decir que la transcripcion no fue buena (no se entendio), podemos pedirle al usuario que repita lo que dijo.
        # speech ya es el texto de lo que dijo, esta transcripto

        log.info(f"Lo que dijo el usuario fue: {str(speech)}")

        # la conversacion deberia estar en memoria para no tardar tiempo. Como va a ser siempre 1 a la vez y no mas, podemos hacerlo
        conversacion = []

        conversacion.append(speech)
        # 3. generar una respuesta
        # respuestaEnTexto = gemini.generarRespuesta(prompt, conversacion)
        respuestaEnTexto = ""

        # 3.1. armar el audio
        data = jsonify({
            "texto": respuestaEnTexto,
            "idVoz": "O1CnH2NGEehfL1nmYACp", # TODO: obtenerlo de la conversacion, del remitente!
            "estabilidad": 0.5,
            "velocidad": "normal"
        })
        audio = ElevenLabsController.generarTTS(data)
        
        # 3.2. exponer audio en internet
        urlAudio = None # enviarAudio(audio)

        # 4. enviar a twilio un audio con la respuesta
        response = VoiceResponse()
        response.play(urlAudio)

        response.gather(
            input="speech",
            timeout=5,
            action="https://a552b2577df7.ngrok-free.app/api/twilio/respuesta" # TODO: este endpoint es nuestro. Cuando pase al despliegue se debe cambiar 
        )
        
        return Response(str(response), mimetype="text/xml")
