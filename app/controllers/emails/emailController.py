import datetime
import re

from flask import jsonify
from app.backend.models import RegistroEvento
from app.backend.models.error import responseError
from app.backend.models.evento import Evento
from app.backend.models.resultadoEvento import ResultadoEvento
from app.backend.models.tipoEvento import TipoEvento
from app.config.db_config import SessionLocal
from app.backend.apis.twilio.sendgrid import enviarMail as enviarMailTwilio
from app.backend.apis.smtp.smtpconnection import SMTPConnection
from app.controllers.emails.aiController import AIController
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

    @staticmethod
    def generarYEnviarMail(data):
        if not data or "proveedor" not in data or "destinatarios" not in data or "remitente" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios como 'proveedor', 'destinatarios' o 'remitente'", 400)

        proveedor = data["proveedor"]
        destinatarios = data["destinatarios"]
        remitente = data["remitente"]

        contexto = (
            "Armame un email del estilo Phishing avisando a los empleados que hay una compra no reconocida. "
            "Que el cuerpo sea en formato html y tenga un botón 'Haz clic aquí' que te envíe a "
            "'http://localhost:8080/registro'. Dame la respuesta en formato json con asunto y cuerpo asi mi codigo puede interpretarlo. "
            "el json generado debe tener literalmente los nombres asunto y cuerpo, porque sino el codigo no lo puede interpretar"
        )

        try:
            # Llamada a Gemini para generar asunto y cuerpo
            texto_generado, _ = AIController.armarEmailGemini({"contexto": contexto})
            logger.info(texto_generado)
            texto_generado = re.sub(r"```(?:json)?", "", texto_generado).strip()
            logger.info(texto_generado)
            import json
            try:
                email_generado = json.loads(texto_generado)
                asunto = email_generado.get("asunto")
                cuerpo = email_generado.get("cuerpo")
            except Exception:
                return responseError("ERROR_JSON", "La respuesta de Gemini no es un JSON válido con 'asunto' y 'cuerpo'", 500)

            if not asunto or not cuerpo:
                return responseError("ERROR_DATOS_GENERADOS", "No se pudo extraer asunto o cuerpo del contenido generado", 500)

            # Guardar en DB
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

            # Envío según proveedor
            if proveedor == "twilio":
                response = enviarMailTwilio(asunto, cuerpo, destinatarios)
                logger.success(f"Twilio sendgrid response: {response.status_code}")
            elif proveedor == "smtp":
                smtp = SMTPConnection("casarivadavia.ddns.net", "40587")
                smtp.login("marcos", "linuxcasa")
                message = smtp.compose_message(
                    sender=remitente,
                    name="Administración PhishIntel",
                    recipients=destinatarios,
                    subject=asunto,
                    html=cuerpo
                )
                smtp.send_mail(message)
            else:
                session.rollback()
                return responseError("PROVEEDOR_INVALIDO", "Proveedor de correo no reconocido", 400)

            session.close()
            return jsonify({"mensaje": "Email generado y enviado correctamente"}), 201

        except Exception as e:
            session.rollback()
            session.close()
            return responseError("ERROR", f"Hubo un error al generar y enviar el mail: {str(e)}", 500)
