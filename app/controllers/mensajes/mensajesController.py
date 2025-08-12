from flask import jsonify

from app.backend.models.error import responseError
from app.utils.config import get
from app.utils.logger import log
from twilio.rest import Client

account_sid = get("TWILIO_ACCOUNT_SID_IGNA")
auth_token = get("TWILIO_AUTH_TOKEN_IGNA")
# phone = get("TWILIO_PHONE_IGNA")

class MensajesController:

    @staticmethod
    def enviarMensajeWhatsapp(data):
        log.info("Se recibio una solicitud para enviar mensaje via WhatsApp")

        if not data or "remitente" not in data or "destinatario" not in data or "mensaje" not in data:
            log.warn("Faltan campos obligatorios")
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios (remitente, destinatario o mensaje)'", 400)

        try:
            client = Client(account_sid, auth_token)

            message = client.messages.create(
                body=data["mensaje"],
                from_='whatsapp:+14155238886',
                # from_='whatsapp:' + data["remitente"], Comento esta linea porque no se si podremos probar otro remitente lol
                to='whatsapp:' + data["destinatario"]
            )

            log.info("Whatsapp enviado con SID: " + message.sid)

            return jsonify({"mensaje": f"Whatsapp enviado con SID: {message.sid}"}), 201
        except Exception as e:
            log.error("Hubo un error al enviar mensaje por WhatsApp: " + str(e))
            return responseError("ERROR_API", "Hubo un error al enviar mensaje por WhatsApp: " + str(e), 500)


    @staticmethod
    def enviarMensajeSMS(data):
        log.info("Se recibio una solicitud para enviar mensaje via SMS")

        if not data or "remitente" not in data or "destinatario" not in data or "mensaje" not in data:
            log.warn("Faltan campos obligatorios")
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios (remitente, destinatario o mensaje)'", 400)

        try:
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=data["mensaje"],
                from_='+19528009780',
                to=data["destinatario"]
            )

            log.info("SMS enviado con SID: " + message.sid)

            return jsonify({"mensaje": f"SMS enviado con SID: {message.sid}"}), 201
        except Exception as e:
            log.error("Hubo un error al enviar mensaje por WhatsApp: " + str(e))
            return responseError("ERROR_API", "Hubo un error al enviar mensaje por WhatsApp: " + str(e), 500)
