from flask import jsonify
from sqlalchemy.orm import joinedload
from app.backend.models import Evento, RegistroEvento
from app.backend.models.error import responseError
from app.backend.models.resultadoEvento import ResultadoEvento
from app.backend.models.tipoEvento import TipoEvento
from app.config.db_config import SessionLocal
from datetime import datetime

class EventosController:

    @staticmethod
    def obtenerEventos():
        session = SessionLocal()
        try:
            eventos = session.query(Evento).options(
                joinedload(Evento.registroEvento),
                joinedload(Evento.usuarios)
            ).all()

            eventos_a_retornar = [{
                "idEvento": evento.idEvento,
                "tipoEvento": evento.tipoEvento.value,
                "fechaEvento": evento.fechaEvento.isoformat(),
                "resultado": evento.resultado.value,
                "registroEvento": {
                    "idRegistroEvento": evento.registroEvento.idRegistroEvento,
                    "asunto": evento.registroEvento.asunto,
                    "cuerpo": evento.registroEvento.cuerpo
                } if evento.registroEvento else None,
                "usuarios": [usuario.idUsuario for usuario in evento.usuarios]
            } for evento in eventos]

            return jsonify({"eventos": eventos_a_retornar}), 200
        finally:
            session.close()


class EventosController:

    @staticmethod
    def obtenerEventos():
        session = SessionLocal()
        try:
            eventos = session.query(Evento).options(
                joinedload(Evento.registroEvento),
                joinedload(Evento.usuarios)
            ).all()

            eventos_a_retornar = [{
                "idEvento": evento.idEvento,
                "tipoEvento": evento.tipoEvento.value,
                "fechaEvento": evento.fechaEvento.isoformat(),
                "resultado": evento.resultado.value,
                "registroEvento": {
                    "idRegistroEvento": evento.registroEvento.idRegistroEvento,
                    "asunto": evento.registroEvento.asunto,
                    "cuerpo": evento.registroEvento.cuerpo
                } if evento.registroEvento else None,
                "usuarios": [usuario.idUsuario for usuario in evento.usuarios]
            } for evento in eventos]

            return jsonify({"eventos": eventos_a_retornar}), 200
        finally:
            session.close()

    @staticmethod
    def crearEvento(data):
        if not data or "tipoEvento" not in data or "fechaEvento" not in data or "resultado" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios para crear el evento", 400)

        try:
            tipo_evento = data["tipoEvento"]
            if tipo_evento not in [e.value for e in TipoEvento]:
                return responseError("TIPO_EVENTO_INVALIDO", "El tipo de evento no es válido", 400)

            resultado = data["resultado"]
            if resultado not in [r.value for r in ResultadoEvento]:
                return responseError("RESULTADO_INVALIDO", "El resultado del evento no es válido", 400)

            try:
                fecha_evento = datetime.fromisoformat(data["fechaEvento"])
            except ValueError:
                return responseError("FECHA_INVALIDA", "El formato de la fecha no es válido", 400)

            session = SessionLocal()

            # Create new event
            nuevo_evento = Evento(
                tipoEvento=tipo_evento,
                fechaEvento=fecha_evento,
                resultado=resultado
            )

            if "registroEvento" in data:
                registro_evento_data = data["registroEvento"]
                if "asunto" in registro_evento_data or "cuerpo" in registro_evento_data:
                    nuevo_registro_evento = RegistroEvento(
                        asunto=registro_evento_data.get("asunto"),
                        cuerpo=registro_evento_data.get("cuerpo")
                    )
                    nuevo_evento.registroEvento = nuevo_registro_evento

            session.add(nuevo_evento)
            session.commit()
            session.refresh(nuevo_evento)
            session.close()

            return jsonify({"mensaje": "Evento creado correctamente", "idEvento": nuevo_evento.idEvento}), 201

        except Exception as e:
            session.close()
            return responseError("ERROR_CREACION_EVENTO", f"Error al crear el evento: {str(e)}", 500)