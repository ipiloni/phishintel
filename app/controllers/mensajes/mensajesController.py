from flask import jsonify

from app.backend.models.error import responseError
from app.utils.config import get
from twilio.rest import Client

account_sid = get("TWILIO_ACCOUNT_SID_IGNA")
auth_token = get("TWILIO_AUTH_TOKEN_IGNA")
# phone = get("TWILIO_PHONE_IGNA")

class MensajesController:

    @staticmethod
    def enviarMensajeWhatsapp(data):
        if not data or "remitente" not in data or "destinatario" not in data or "mensaje" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios (remitente, destinatario o mensaje)'", 400)

        try:
            client = Client(account_sid, auth_token)

            message = client.messages.create(
                body=data["mensaje"],
                from_='whatsapp:' + data["remitente"],
                to='whatsapp:' + data["destinatario"]
            )

            return jsonify({"mensaje": f"Mensaje enviado con SID: {message.sid}"}), 201
        except Exception as e:
            return responseError("ERROR_API", "Hubo un error al enviar mensaje por WhatsApp: " + str(e), 500)
