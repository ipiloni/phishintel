from flask import jsonify
from twilio.rest import Client

from app.backend.models.error import responseError
from app.utils.config import get
from app.utils.logger import log


class SMSController:
    
    @staticmethod
    def enviarMensajeTwilio(data):
        """
        Envía un mensaje SMS usando Twilio API.
        
        Args:
            data (dict): Diccionario con los siguientes campos:
                - mensaje (str): Mensaje a enviar
                - destinatario (str): Número de teléfono del destinatario
                
        Returns:
            tuple: (response, status_code)
        """
        log.info("Se recibió una solicitud para enviar mensaje via SMS")

        if not data or "mensaje" not in data or "destinatario" not in data:
            log.warn("Faltan campos obligatorios")
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios (mensaje o destinatario)", 400)

        try:
            account_sid = get("TWILIO_ACCOUNT_SID_IGNA")
            auth_token = get("TWILIO_AUTH_TOKEN_IGNA")
            
            if not account_sid or not auth_token:
                log.error("Credenciales de Twilio no configuradas")
                return responseError("CREDENCIALES_NO_CONFIGURADAS", "Credenciales de Twilio no configuradas", 500)

            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=data["mensaje"],
                from_='+19528009780',
                to=data["destinatario"]
            )

            log.info("SMS enviado con SID: " + message.sid)

            return jsonify({"mensaje": f"SMS enviado con SID: {message.sid}"}), 201
        except Exception as e:
            log.error("Hubo un error al enviar mensaje por SMS: " + str(e))
            return responseError("ERROR_API", "Hubo un error al enviar mensaje por SMS: " + str(e), 500)
