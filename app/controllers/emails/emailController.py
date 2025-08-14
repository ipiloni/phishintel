import datetime
import re

from flask import jsonify
from app.backend.models import RegistroEvento, Usuario
from app.backend.models.error import responseError
from app.backend.models.evento import Evento
from app.backend.models.resultadoEvento import ResultadoEvento
from app.backend.models.tipoEvento import TipoEvento
from app.backend.models.usuarioxevento import UsuarioxEvento
from app.config.db_config import SessionLocal
from app.backend.apis.twilio.sendgrid import enviarMail as enviarMailTwilio
from app.backend.apis.smtp.smtpconnection import SMTPConnection
from app.controllers.emails.aiController import AIController
from app.utils.logger import log


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
            registroEvento:RegistroEvento = RegistroEvento(asunto=asunto, cuerpo=cuerpo)
            evento = Evento(
                tipoEvento=TipoEvento.CORREO,
                fechaEvento=datetime.datetime.now(),
                registroEvento=registroEvento
            )

            session = SessionLocal()
            session.add(evento)
            session.commit()

            # Envío del mail según proveedor
            if proveedor == "twilio":
                response = enviarMailTwilio(asunto, cuerpo, destinatario)
                log.info(f"Respuesta del servicio Twilio sendgrid: {response.status_code}")
            elif proveedor == "smtp":
                smtp = SMTPConnection("casarivadavia.ddns.net", "40587")
                smtp.login("marcos", "linuxcasa")
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
            log.error(f"Hubo un error al intentar enviar el email: {str(e)}")
            session.rollback()
            session.close()
            return responseError("ERROR", f"Hubo un error al enviar mail: {str(e)}", 500)

    @staticmethod
    def generarYEnviarMail(data):
        if not data or "proveedor" not in data or "idUsuario" not in data or "remitente" not in data:
            return responseError("CAMPOS_OBLIGATORIOS",
                                 "Faltan campos obligatorios como 'proveedor', 'idUsuario' o 'remitente'", 400)

        proveedor = data["proveedor"]
        id_usuario = data["idUsuario"]
        remitente = data["remitente"]

        session = SessionLocal()
        try:
            # Buscar el usuario para obtener su email
            usuario = session.query(Usuario).filter_by(idUsuario=id_usuario).first()
            if not usuario or not usuario.correo:
                session.close()
                return responseError("USUARIO_NO_ENCONTRADO", "No se encontró el usuario o no tiene correo registrado",
                                     404)

            # Creamos el evento
            registroEvento = RegistroEvento()
            evento = Evento(
                tipoEvento=TipoEvento.CORREO,
                fechaEvento=datetime.datetime.now(),
                registroEvento=registroEvento
            )
            session.add(evento)
            session.commit()  # Para obtener idEvento

            # Creamos registro en usuariosxeventos
            usuario_evento = UsuarioxEvento(
                idUsuario=id_usuario,
                idEvento=evento.idEvento,
                resultado=ResultadoEvento.PENDIENTE
            )
            session.add(usuario_evento)
            session.commit()

            # Contexto para IA con enlace personalizado
            link_falla = f"http://localhost:8080/api/sumar-falla?idUsuario={id_usuario}&idEvento={evento.idEvento}"
            contexto = (
                "Armame un email del estilo Phishing avisando que hay una compra no reconocida. "
                f"El cuerpo debe ser HTML con un botón 'Haz clic aquí' que apunte a '{link_falla}'. "
                "Devuelve en formato JSON con las claves 'asunto' y 'cuerpo'."
            )

            # Llamada a Gemini
            texto_generado, _ = AIController.armarEmail({"contexto": contexto})
            texto_generado = re.sub(r"```(?:json)?", "", texto_generado).strip()

            import json
            try:
                email_generado = json.loads(texto_generado)
                asunto = email_generado.get("asunto")
                cuerpo = email_generado.get("cuerpo")
            except Exception:
                session.rollback()
                session.close()
                return responseError("ERROR_JSON",
                                     "La respuesta de Gemini no es un JSON válido con 'asunto' y 'cuerpo'", 500)

            # Guardar asunto y cuerpo en registroEvento
            registroEvento.asunto = asunto
            registroEvento.cuerpo = cuerpo
            session.commit()

            # Enviar el email
            if proveedor == "twilio":
                response = enviarMailTwilio(asunto, cuerpo, usuario.correo)
                log.success(f"Twilio sendgrid response: {response.status_code}")
            elif proveedor == "smtp":
                smtp = SMTPConnection("casarivadavia.ddns.net", "40587")
                smtp.login("marcos", "linuxcasa")
                message = smtp.compose_message(
                    sender=remitente,
                    name="Administración PhishIntel",
                    recipients=[usuario.correo],
                    subject=asunto,
                    html=cuerpo
                )
                smtp.send_mail(message)
            else:
                session.rollback()
                return responseError("PROVEEDOR_INVALIDO", "Proveedor de correo no reconocido", 400)

            idnuevo = evento.idEvento
            session.close()
            return jsonify({"mensaje": "Email generado y enviado correctamente", "idEvento": idnuevo}), 201

        except Exception as e:
            session.rollback()
            session.close()
            return responseError("ERROR", f"Hubo un error al generar y enviar el mail: {str(e)}", 500)
