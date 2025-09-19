from flask import jsonify, request
from sqlalchemy.orm import joinedload
from app.backend.models import Evento, RegistroEvento, UsuarioxEvento, Usuario
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
                joinedload(Evento.usuariosAsociados).joinedload(UsuarioxEvento.usuario)
            ).all()

            eventos_a_retornar = []
            for evento in eventos:
                usuarios_info = []
                for ux in evento.usuariosAsociados:
                    usuario_data = {
                        "idUsuario": ux.usuario.idUsuario,
                        "nombreUsuario": ux.usuario.nombreUsuario,
                        "resultado": ux.resultado.value
                    }
                    # Agregar fechas si existen
                    if ux.fecha_reporte:
                        usuario_data["fecha_reporte"] = ux.fecha_reporte.isoformat()
                    if ux.fecha_falla:
                        usuario_data["fecha_falla"] = ux.fecha_falla.isoformat()
                    
                    usuarios_info.append(usuario_data)

                eventos_a_retornar.append({
                    "idEvento": evento.idEvento,
                    "tipoEvento": evento.tipoEvento.value,
                    "fechaEvento": evento.fechaEvento.isoformat(),
                    "registroEvento": {
                        "idRegistroEvento": evento.registroEvento.idRegistroEvento,
                        "asunto": evento.registroEvento.asunto,
                        "cuerpo": evento.registroEvento.cuerpo
                    } if evento.registroEvento else None,
                    "usuarios": usuarios_info
                })

            return jsonify({"eventos": eventos_a_retornar}), 200
        finally:
            session.close()


    @staticmethod
    def obtenerEventoPorId(idEvento):
        session = SessionLocal()
        try:
            evento = session.query(Evento).options(
                joinedload(Evento.registroEvento),
                joinedload(Evento.usuariosAsociados).joinedload(UsuarioxEvento.usuario)
            ).filter_by(idEvento=idEvento).first()

            if not evento:
                return responseError("EVENTO_NO_ENCONTRADO", "No se encontró el evento", 404)

            usuarios_info = []
            for ux in evento.usuariosAsociados:
                usuario_data = {
                    "idUsuario": ux.usuario.idUsuario,
                    "nombreUsuario": ux.usuario.nombreUsuario,
                    "resultado": ux.resultado.value
                }
                # Agregar fechas si existen
                if ux.fecha_reporte:
                    usuario_data["fecha_reporte"] = ux.fecha_reporte.isoformat()
                if ux.fecha_falla:
                    usuario_data["fecha_falla"] = ux.fecha_falla.isoformat()
                
                usuarios_info.append(usuario_data)

            evento_info = {
                "idEvento": evento.idEvento,
                "tipoEvento": evento.tipoEvento.value,
                "fechaEvento": evento.fechaEvento.isoformat(),
                "registroEvento": {
                    "idRegistroEvento": evento.registroEvento.idRegistroEvento,
                    "asunto": evento.registroEvento.asunto,
                    "cuerpo": evento.registroEvento.cuerpo
                } if evento.registroEvento else None,
                "usuarios": usuarios_info
            }

            return jsonify(evento_info), 200
        finally:
            session.close()


    @staticmethod
    def crearEvento(data):
        if not data or "tipoEvento" not in data or "fechaEvento" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios para crear el evento", 400)

        try:
            tipo_evento_val = data["tipoEvento"]
            if tipo_evento_val not in [e.value for e in TipoEvento]:
                return responseError("TIPO_EVENTO_INVALIDO", "El tipo de evento no es válido", 400)

            fecha_evento_str = data["fechaEvento"]
            try:
                fecha_evento = datetime.fromisoformat(fecha_evento_str)
            except ValueError:
                return responseError("FECHA_INVALIDA", "El formato de la fecha no es válido", 400)


            session = SessionLocal()

            nuevo_evento = Evento(
                tipoEvento=tipo_evento_val,
                fechaEvento=fecha_evento
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

            idevento = nuevo_evento.idEvento
            session.close()
            return jsonify({"mensaje": "Evento creado correctamente", "idEvento": idevento}), 201

        except Exception as e:
            session.close()
            return responseError("ERROR_CREACION_EVENTO", f"Error al crear el evento: {str(e)}", 500)


    @staticmethod
    def editarEvento(idEvento, data):
        if not data:
            return responseError("DATOS_VACIOS", "No se enviaron datos para modificar", 400)

        session = SessionLocal()
        try:
            evento = session.query(Evento).filter_by(idEvento=idEvento).first()
            if not evento:
                return responseError("EVENTO_NO_ENCONTRADO", "No se encontró el evento a modificar", 404)

            if "tipoEvento" in data:
                tipo_evento_val = data["tipoEvento"]
                if tipo_evento_val not in [e.value for e in TipoEvento]:
                    return responseError("TIPO_EVENTO_INVALIDO", "El tipo de evento no es válido", 400)
                evento.tipoEvento = tipo_evento_val

            if "fechaEvento" in data:
                try:
                    evento.fechaEvento = datetime.fromisoformat(data["fechaEvento"])
                except ValueError:
                    return responseError("FECHA_INVALIDA", "El formato de la fecha no es válido", 400)


            if "registroEvento" in data:
                registro_evento_data = data["registroEvento"]
                if evento.registroEvento is None:
                    evento.registroEvento = RegistroEvento()
                if "asunto" in registro_evento_data:
                    evento.registroEvento.asunto = registro_evento_data["asunto"]
                if "cuerpo" in registro_evento_data:
                    evento.registroEvento.cuerpo = registro_evento_data["cuerpo"]

            session.commit()
            session.close()
            return jsonify({"mensaje": "Evento modificado correctamente"}), 200

        except Exception as e:
            session.close()
            return responseError("ERROR_MODIFICACION_EVENTO", f"Error al modificar el evento: {str(e)}", 500)


    @staticmethod
    def asociarUsuarioEvento(idEvento, idUsuario, resultado_val, fecha_reporte=None, fecha_falla=None):
        if resultado_val not in [r.value for r in ResultadoEvento]:
            return responseError("RESULTADO_INVALIDO", "El resultado del evento no es válido", 400)

        session = SessionLocal()
        try:
            evento = session.query(Evento).filter_by(idEvento=idEvento).first()
            if not evento:
                return responseError("EVENTO_NO_ENCONTRADO", "No se encontró el evento", 404)

            usuario = session.query(Usuario).filter_by(idUsuario=idUsuario).first()
            if not usuario:
                return responseError("USUARIO_NO_ENCONTRADO", "No se encontró el usuario", 404)

            # Verificar si la asociación ya existe
            usuario_evento = session.query(UsuarioxEvento).filter_by(
                idEvento=idEvento,
                idUsuario=idUsuario
            ).first()

            if usuario_evento:
                usuario_evento.resultado = ResultadoEvento(resultado_val)
                if fecha_reporte:
                    usuario_evento.fecha_reporte = fecha_reporte
                if fecha_falla:
                    usuario_evento.fecha_falla = fecha_falla
            else:
                usuario_evento = UsuarioxEvento(
                    idEvento=idEvento,
                    idUsuario=idUsuario,
                    resultado=ResultadoEvento(resultado_val),
                    fecha_reporte=fecha_reporte,
                    fecha_falla=fecha_falla
                )
                session.add(usuario_evento)

            session.commit()
            session.close()
            return jsonify({"mensaje": "Usuario asociado al evento correctamente"}), 200

        except Exception as e:
            session.close()
            return responseError("ERROR_ASOCIAR_USUARIO_EVENTO", f"Error al asociar usuario al evento: {str(e)}", 500)


    @staticmethod
    def eliminarEvento(idEvento):
        session = SessionLocal()
        try:
            evento = session.query(Evento).filter_by(idEvento=idEvento).first()

            if not evento:
                return responseError("EVENTO_NO_ENCONTRADO", "El evento no existe", 404)

            # Borrar asociaciones usuarioxevento
            session.query(UsuarioxEvento).filter_by(idEvento=idEvento).delete()

            # Opcional: borrar registroEvento asociado si existe
            if evento.registroEvento:
                session.delete(evento.registroEvento)

            # Borrar evento
            session.delete(evento)
            session.commit()
            return jsonify({"mensaje": "Evento eliminado correctamente"}), 200
        except Exception as e:
            session.rollback()
            return responseError("ERROR", f"No se pudo eliminar el evento: {str(e)}", 500)
        finally:
            session.close()
