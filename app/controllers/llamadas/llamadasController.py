from app.backend.apis.twilio import twilio
from app.backend.models.error import responseError

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
    # def procesarRespuesta(algoDeTwilio):
    #     # informacion = lo que responde la persona = lo que te da twilio de llamada ahora.
    #     # 1. procesar esta info
    #     # 2. anidar esta informacion (en formato texto) a la conversacion (sumarlo a la lista conversacion)
    #     # 3. generar una respuesta
    #     # 4. enviar a twilio un audio con la respuesta

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