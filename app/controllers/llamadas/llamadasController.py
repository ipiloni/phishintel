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