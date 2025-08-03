import datetime
from flask import jsonify
from app.backend.models import RegistroEvento
from app.backend.models.error import responseError
from app.backend.models.evento import Evento
from app.backend.models.resultadoEvento import ResultadoEvento
from app.backend.models.tipoEvento import TipoEvento
from app.config.db_config import SessionLocal
from app.backend.apis.twilio.sendgrid import enviarMail as enviarMailTwilio
from app.backend.apis.smtp.smtpconnection import SMTPConnection  # Ruta al archivo que compartiste
from app.utils import logger  # Asegurate de que logger esté disponible

class EmailController:

    @staticmethod
    def enviarMail(data):
        if not data or "destinatario" not in data or "asunto" not in data or "cuerpo" not in data or "proveedor" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios como 'destinatario', 'asunto', 'cuerpo' o 'proveedor'", 400)

        destinatario = data["destinatario"]
        asunto = data["asunto"]
        cuerpo = data["cuerpo"]
        proveedor = data["proveedor"]  # "twilio" o "smtp"

        try:
            # Guardar evento y registro en DB
            registroEvento = RegistroEvento(asunto=asunto, cuerpo=cuerpo)
            evento = Evento(
                tipoEvento=TipoEvento.CORREO,
                fechaEvento=datetime.datetime.now(),
                resultado=ResultadoEvento.PENDIENTE,
                registroEvento=registroEvento
            )

            session = SessionLocal()
            session.add(evento)
            session.commit()

            # Envío del mail según proveedor
            if proveedor == "twilio":
                response = enviarMailTwilio(asunto, cuerpo, destinatario)
                logger.success(f"Twilio sendgrid response: {response.status_code}")
            elif proveedor == "smtp":
                logger.info("Estamos mandando un mail por el smtp")
                smtp = SMTPConnection("casarivadavia.ddns.net", "40587")
                logger.info("esta es la conexion")
                smtp.login("marcos", "linuxcasa")
                logger.info("nos hemos logueado")
                message = smtp.compose_message(
                    sender="marcos@phishintel.org",
                    name="Marcos",
                    recipients=[destinatario],
                    subject=asunto,
                    html=cuerpo
                )
                smtp.send_mail(message)
            else:
                session.rollback()
                return responseError("PROVEEDOR_INVALIDO", "Proveedor de correo no reconocido", 400)

            session.close()
            return jsonify({"mensaje": "Email enviado correctamente"}), 201

        except Exception as e:
            session.rollback()
            session.close()
            return responseError("ERROR", f"Hubo un error al enviar mail: {str(e)}", 500)
