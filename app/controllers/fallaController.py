from flask import jsonify
from app.backend.models.error import responseError
from app.backend.models.resultadoEvento import ResultadoEvento
from app.backend.models.usuarioxevento import UsuarioxEvento
from app.config.db_config import SessionLocal

# Variable global para contar fallas
conteo_fallas = {"total": 0}

class FallaController:

    @staticmethod
    def sumarFalla(idUsuario, idEvento):
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
            session.commit()

            return jsonify({"mensaje": "Falla registrada", "idUsuario": idUsuario, "idEvento": idEvento}), 200

        except Exception as e:
            session.rollback()
            return responseError("ERROR", f"No se pudo registrar la falla: {str(e)}", 500)
        finally:
            session.close()