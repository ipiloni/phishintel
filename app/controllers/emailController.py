import datetime

from flask import jsonify

from app.backend.apis.twilio.sendgrid import enviarMail
from app.backend.models import RegistroEvento
from app.backend.models.error import responseError
from app.backend.models.evento import Evento
from app.backend.models.resultadoEvento import ResultadoEvento
from app.backend.models.tipoEvento import TipoEvento
from app.config.db_config import SessionLocal

class EmailController:

    @staticmethod
    def enviarMail(data):
        if not data or "destinatario" not in data or "asunto" not in data or "cuerpo" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'destinatario', 'asunto' o 'cuerpo'", 400)

        destinatario = data["destinatario"]
        asunto = data["asunto"]
        cuerpo = data["cuerpo"]

        try:

            registroEvento = RegistroEvento(
                asunto=asunto,
                cuerpo=cuerpo
            )

            evento = Evento(
                tipoEvento=TipoEvento.CORREO,
                fechaEvento=datetime.datetime.now(),
                resultado=ResultadoEvento.PENDIENTE,
                registroEvento=registroEvento
            )

            session = SessionLocal()
            session.add(evento)
            session.commit()
            session.close()

            response = enviarMail(asunto, cuerpo, destinatario)

            print(response.status_code)
            print(response.body)
            print(response.headers)

            return jsonify({"mensaje": "Email enviado correctamente"}), 201

        except Exception as e:
            return responseError("ERROR", f"Hubo un error al enviar mail: {str(e)}", 500)