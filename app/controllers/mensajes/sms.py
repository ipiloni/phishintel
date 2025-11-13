from flask import jsonify
from twilio.rest import Client
import requests

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

    @staticmethod
    def enviarMensajeTextBee(data):
        """
        Envía un mensaje SMS usando TextBee API.
        
        Args:
            data (dict): Diccionario con los siguientes campos:
                - mensaje (str): Mensaje a enviar
                - destinatario (str): Número de teléfono del destinatario
                
        Returns:
            tuple: (response, status_code)
        """
        log.info("Se recibió una solicitud para enviar mensaje via SMS con TextBee")

        if not data or "mensaje" not in data or "destinatario" not in data:
            log.warn("Faltan campos obligatorios")
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios (mensaje o destinatario)", 400)

        try:
            token = get("TEXTBEE_TOKEN")
            device_id = get("TEXTBEE_DEVICE_ID")
            
            if not token:
                log.error("Token de TextBee no configurado")
                return responseError("CREDENCIALES_NO_CONFIGURADAS", "Token de TextBee no configurado", 500)
            
            if not device_id:
                log.error("Device ID de TextBee no configurado")
                return responseError("CREDENCIALES_NO_CONFIGURADAS", "Device ID de TextBee no configurado. Agrega TEXTBEE_DEVICE_ID en properties.env", 500)

            # URL de la API de TextBee - Formato correcto según documentación
            url = f"https://api.textbee.dev/api/v1/gateway/devices/{device_id}/send-sms"

            # Headers para la petición - TextBee usa x-api-key
            headers = {
                "x-api-key": token,
                "Content-Type": "application/json"
            }

            # Datos del mensaje - Formato correcto según documentación
            payload = {
                "recipients": [data["destinatario"]],
                "message": data["mensaje"]
            }

            log.info(f"Enviando SMS a {data['destinatario']} via TextBee")
            log.info(f"URL: {url}")
            log.info(f"Payload: {payload}")

            # Realizar la petición POST
            response = requests.post(url, json=payload, headers=headers, timeout=30)

            # Logging detallado de la respuesta
            log.info(f"Status code: {response.status_code}")
            log.info(f"Response headers: {response.headers}")
            log.info(f"Response text: {response.text}")

            if response.status_code == 200:
                response_data = response.json()
                log.info(f"SMS enviado correctamente via TextBee. ID: {response_data.get('id', 'N/A')}")
                return jsonify({
                    "mensaje": "SMS enviado correctamente via TextBee",
                    "destinatario": data["destinatario"],
                    "contenido": data["mensaje"],
                    "id": response_data.get('id', 'N/A')
                }), 201
            else:
                error_msg = f"Error en TextBee API: {response.status_code} - {response.text}"
                log.error(error_msg)
                return responseError("ERROR_API_TEXTBEE", error_msg, response.status_code)

        except requests.exceptions.Timeout:
            log.error("Timeout al enviar mensaje via TextBee")
            return responseError("TIMEOUT_ERROR", "Timeout al enviar mensaje via TextBee", 408)
        except requests.exceptions.ConnectionError as e:
            log.error(f"Error de conexión al enviar mensaje via TextBee: {str(e)}")
            return responseError("CONNECTION_ERROR", f"Error de conexión al enviar mensaje via TextBee: {str(e)}", 503)
        except Exception as e:
            log.error("Hubo un error al enviar mensaje por SMS via TextBee: " + str(e))
            return responseError("ERROR_API", "Hubo un error al enviar mensaje por SMS via TextBee: " + str(e), 500)
