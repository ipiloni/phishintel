from flask import jsonify
from datetime import datetime
from app.backend.models.error import responseError
from app.backend.models.resultadoEvento import ResultadoEvento
from app.backend.models.usuarioxevento import UsuarioxEvento
from app.config.db_config import SessionLocal
from app.utils.logger import log

# Variable global para contar fallas
conteo_fallas = {"total": 0}

class ResultadoEventoController:

    @staticmethod
    def sumarFalla(idUsuario, idEvento, fechaFalla=None):
        session = SessionLocal()
        try:
            # Buscar relación usuario-evento
            usuario_evento = session.query(UsuarioxEvento).filter_by(
                idUsuario=idUsuario,
                idEvento=idEvento
            ).first()

            if not usuario_evento:
                session.close()
                return responseError("RELACION_NO_ENCONTRADA", "No existe relación entre el usuario y el evento", 404)

            # Actualizar a FALLA
            usuario_evento.resultado = ResultadoEvento.FALLA
            # Si no se proporciona fecha, usar la fecha actual
            if fechaFalla is None:
                fechaFalla = datetime.now()
            usuario_evento.fechaFalla = fechaFalla
            session.commit()

            return jsonify({
                "mensaje": "Falla registrada", 
                "idUsuario": idUsuario, 
                "idEvento": idEvento,
                "fechaFalla": fechaFalla.isoformat()
            }), 200

        except Exception as e:
            log.error("Hubo un error al intentar sumar la falla: " + str(e))
            session.rollback()
            return responseError("ERROR", f"No se pudo registrar la falla: {str(e)}", 500)
        finally:
            session.close()

    @staticmethod
    def sumarReportado(idUsuario, idEvento, fechaReporte=None):
        session = SessionLocal()
        try:
            # Buscar relación usuario-evento
            usuario_evento = session.query(UsuarioxEvento).filter_by(
                idUsuario=idUsuario,
                idEvento=idEvento
            ).first()

            if not usuario_evento:
                session.close()
                return responseError("RELACION_NO_ENCONTRADA", "No existe relación entre el usuario y el evento", 404)

            # Actualizar a REPORTADO
            usuario_evento.resultado = ResultadoEvento.REPORTADO
            # Si no se proporciona fecha, usar la fecha actual
            if fechaReporte is None:
                fechaReporte = datetime.now()
            usuario_evento.fechaReporte = fechaReporte
            session.commit()

            return jsonify({
                "mensaje": "Reporte registrado", 
                "idUsuario": idUsuario, 
                "idEvento": idEvento,
                "fechaReporte": fechaReporte.isoformat()
            }), 200

        except Exception as e:
            log.error("Hubo un error al intentar sumar el reporte: " + str(e))
            session.rollback()
            return responseError("ERROR", f"No se pudo registrar el reporte: {str(e)}", 500)
        finally:
            session.close()
