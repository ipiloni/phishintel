from flask import jsonify, request
from sqlalchemy.orm import joinedload
from app.backend.models import Evento, RegistroEvento, UsuarioxEvento, Usuario
from app.backend.models.error import responseError
from app.backend.models.resultadoEvento import ResultadoEvento
from app.backend.models.tipoEvento import TipoEvento
from app.config.db_config import SessionLocal
from datetime import datetime

from app.utils.logger import log


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
                        "resultado": ux.resultado.value,
                        "haFalladoEnElPasado": ux.haFalladoEnElPasado
                    }
                    # Agregar fechas si existen
                    if ux.fechaReporte:
                        usuario_data["fechaReporte"] = ux.fechaReporte.isoformat()
                    if ux.fechaFalla:
                        usuario_data["fechaFalla"] = ux.fechaFalla.isoformat()
                    
                    usuarios_info.append(usuario_data)

                eventos_a_retornar.append({
                    "idEvento": evento.idEvento,
                    "tipoEvento": evento.tipoEvento.value,
                    "fechaEvento": evento.fechaEvento.isoformat(),
                    "registroEvento": {
                        "idRegistroEvento": evento.registroEvento.idRegistroEvento,
                        "asunto": evento.registroEvento.asunto,
                        "cuerpo": evento.registroEvento.cuerpo,
                        "objetivo": evento.registroEvento.objetivo,
                        "conversacion": evento.registroEvento.conversacion
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
                    "resultado": ux.resultado.value,
                    "haFalladoEnElPasado": ux.haFalladoEnElPasado
                }
                # Agregar fechas si existen
                if ux.fechaReporte:
                    usuario_data["fechaReporte"] = ux.fechaReporte.isoformat()
                if ux.fechaFalla:
                    usuario_data["fechaFalla"] = ux.fechaFalla.isoformat()
                
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
        if not data or "tipoEvento" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios para crear el evento", 400)

        session = None
        try:
            tipo_evento_val = data["tipoEvento"]
            if tipo_evento_val not in [e.value for e in TipoEvento]:
                log.error(f"Tipo de evento no es valido")
                return responseError("TIPO_EVENTO_INVALIDO", "El tipo de evento no es válido", 400)

            fecha_evento_str = data["fechaEvento"]
            try:
                fecha_evento = datetime.fromisoformat(fecha_evento_str)

                if data["fechaEvento"] is None:
                    fecha_evento = datetime.now().isoformat()

            except ValueError:
                log.error(f"Fecha no es valida")
                return responseError("FECHA_INVALIDA", "El formato de la fecha no es válido", 400)

            session = SessionLocal()

            nuevo_evento = Evento(
                tipoEvento=tipo_evento_val,
                fechaEvento=fecha_evento
            )

            if "registroEvento" in data:
                registro_evento_data = data["registroEvento"]
                if "asunto" in registro_evento_data or "cuerpo" in registro_evento_data or "objetivo" in registro_evento_data or "conversacion" in registro_evento_data:
                    nuevo_registro_evento = RegistroEvento(
                        asunto=registro_evento_data.get("asunto"),
                        cuerpo=registro_evento_data.get("cuerpo"),
                        objetivo=registro_evento_data.get("objetivo"),
                        conversacion=registro_evento_data.get("conversacion")
                    )
                    nuevo_evento.registroEvento = nuevo_registro_evento

            session.add(nuevo_evento)
            session.commit()
            session.refresh(nuevo_evento)

            idevento = nuevo_evento.idEvento
            session.close()
            log.info(f"Evento creado correctamente con el ID: {idevento}")
            return jsonify({"mensaje": "Evento creado correctamente", "idEvento": idevento}), 201

        except Exception as e:
            if session is not None:
                try:
                    session.rollback()
                    session.close()
                except Exception:
                    pass
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
                if "conversacion" in registro_evento_data:
                    evento.registroEvento.conversacion = registro_evento_data["conversacion"]

            session.commit()
            session.close()
            return jsonify({"mensaje": "Evento modificado correctamente"}), 200

        except Exception as e:
            session.close()
            return responseError("ERROR_MODIFICACION_EVENTO", f"Error al modificar el evento: {str(e)}", 500)


    @staticmethod
    def asociarUsuarioEvento(idEvento, idUsuario, resultado_val, fechaReporte=None, fechaFalla=None):
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
                if fechaReporte:
                    usuario_evento.fechaReporte = fechaReporte
                if fechaFalla:
                    usuario_evento.fechaFalla = fechaFalla
                # Marcar haFalladoEnElPasado si el resultado es FALLA
                if ResultadoEvento(resultado_val) == ResultadoEvento.FALLA:
                    usuario_evento.haFalladoEnElPasado = True
            else:
                usuario_evento = UsuarioxEvento(
                    idEvento=idEvento,
                    idUsuario=idUsuario,
                    resultado=ResultadoEvento(resultado_val),
                    fechaReporte=fechaReporte,
                    fechaFalla=fechaFalla,
                    haFalladoEnElPasado=(ResultadoEvento(resultado_val) == ResultadoEvento.FALLA)
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

    @staticmethod
    def crearBatchEventos(data):
        """
        Crear un batch de eventos y resultados de prueba basado en datos recibidos
        """
        from app.config.db_config import SessionLocal
        from app.backend.models.evento import Evento
        from app.backend.models.registroEvento import RegistroEvento
        from app.backend.models.usuarioxevento import UsuarioxEvento
        from app.backend.models.resultadoEvento import ResultadoEvento
        from app.backend.models.tipoEvento import TipoEvento
        from datetime import datetime, timedelta
        import random
        
        session = SessionLocal()
        
        try:
            # Obtener datos del request
            eventos_data = data.get("eventos", [])
            usuarios_objetivo = data.get("usuarios", list(range(1, 10)))  # Por defecto usuarios 1-9
            
            if not eventos_data:
                return responseError("CAMPOS_OBLIGATORIOS", "Se requiere al menos un evento en el array 'eventos'", 400)
            
            eventos_creados = []
            resultados_creados = []
            
            for evento_data in eventos_data:
                # Validar datos del evento
                if not evento_data.get("tipoEvento") or not evento_data.get("asunto"):
                    continue
                
                # Crear evento
                evento = Evento(
                    tipoEvento=TipoEvento(evento_data["tipoEvento"]),
                    fechaEvento=datetime.fromisoformat(evento_data["fechaEvento"])
                )
                session.add(evento)
                session.flush()  # Para obtener el ID
                
                # Crear registro del evento
                registro = RegistroEvento(
                    idEvento=evento.idEvento,
                    asunto=evento_data["asunto"],
                    cuerpo=evento_data.get("cuerpo"),
                    mensaje=evento_data.get("mensaje")
                )
                session.add(registro)
                
                # Obtener usuarios para este evento (si no se especifica, usar todos)
                usuarios_evento = evento_data.get("usuarios", usuarios_objetivo)
                
                # Crear resultados para usuarios
                for idUsuario in usuarios_evento:
                    # Determinar resultado basado en probabilidades o configuración
                    rand = random.random()
                    
                    # Usuarios 7, 8, 9 tienen más probabilidad de reportar eventos
                    if idUsuario in [7, 8, 9]:
                        if rand < 0.1:  # 10% falla activa
                            resultado = ResultadoEvento.FALLA
                            fechaFalla = evento.fechaEvento + timedelta(minutes=random.randint(5, 60))
                            fechaReporte = None
                            haFalladoEnElPasado = True
                        elif rand < 0.3:  # 20% reportado con falla previa
                            resultado = ResultadoEvento.REPORTADO
                            fechaFalla = evento.fechaEvento + timedelta(minutes=random.randint(5, 30))
                            fechaReporte = evento.fechaEvento + timedelta(minutes=random.randint(10, 120))
                            haFalladoEnElPasado = True
                        elif rand < 0.8:  # 50% reportado SIN falla previa - muy probable
                            resultado = ResultadoEvento.REPORTADO
                            fechaFalla = None
                            fechaReporte = evento.fechaEvento + timedelta(minutes=random.randint(5, 60))
                            haFalladoEnElPasado = False
                        else:  # 20% pendiente (sin falla)
                            resultado = ResultadoEvento.PENDIENTE
                            fechaFalla = None
                            fechaReporte = None
                            haFalladoEnElPasado = False
                    else:
                        # Usuarios 1-6 tienen distribución normal
                        if rand < 0.4:  # 40% falla activa
                            resultado = ResultadoEvento.FALLA
                            fechaFalla = evento.fechaEvento + timedelta(minutes=random.randint(5, 60))
                            fechaReporte = None
                            haFalladoEnElPasado = True
                        elif rand < 0.6:  # 20% reportado (falla pasada)
                            resultado = ResultadoEvento.REPORTADO
                            fechaFalla = evento.fechaEvento + timedelta(minutes=random.randint(5, 30))
                            fechaReporte = evento.fechaEvento + timedelta(minutes=random.randint(10, 120))
                            haFalladoEnElPasado = True
                        else:  # 40% pendiente (sin falla)
                            resultado = ResultadoEvento.PENDIENTE
                            fechaFalla = None
                            fechaReporte = None
                            haFalladoEnElPasado = False
                    
                    # Crear relación usuario-evento
                    usuario_evento = UsuarioxEvento(
                        idUsuario=idUsuario,
                        idEvento=evento.idEvento,
                        resultado=resultado,
                        fechaFalla=fechaFalla,
                        fechaReporte=fechaReporte,
                        haFalladoEnElPasado=haFalladoEnElPasado
                    )
                    session.add(usuario_evento)
                    
                    resultados_creados.append({
                        "idUsuario": idUsuario,
                        "idEvento": evento.idEvento,
                        "resultado": resultado.value,
                        "fechaFalla": fechaFalla.isoformat() if fechaFalla else None,
                        "fechaReporte": fechaReporte.isoformat() if fechaReporte else None,
                        "haFalladoEnElPasado": haFalladoEnElPasado
                    })
                
                eventos_creados.append({
                    "idEvento": evento.idEvento,
                    "tipoEvento": evento.tipoEvento.value,
                    "fechaEvento": evento.fechaEvento.isoformat(),
                    "asunto": evento_data["asunto"],
                    "usuariosAsociados": len(usuarios_evento)
                })
            
            session.commit()
            
            log.info(f"Batch de eventos creado exitosamente: {len(eventos_creados)} eventos, {len(resultados_creados)} resultados")
            
            return jsonify({
                "mensaje": "Batch de eventos creado exitosamente",
                "eventos_creados": len(eventos_creados),
                "resultados_creados": len(resultados_creados),
                "eventos": eventos_creados,
                "resumen_resultados": {
                    "fallas_activas": len([r for r in resultados_creados if r["resultado"] == "FALLA"]),
                    "reportados": len([r for r in resultados_creados if r["resultado"] == "REPORTADO"]),
                    "fallas_pasadas": len([r for r in resultados_creados if r["haFalladoEnElPasado"] and r["resultado"] != "FALLA"]),
                    "pendientes": len([r for r in resultados_creados if r["resultado"] == "PENDIENTE" and not r["haFalladoEnElPasado"]])
                }
            }), 200
            
        except Exception as e:
            session.rollback()
            log.error(f"Error creando batch de eventos: {str(e)}")
            return responseError("ERROR", f"No se pudo crear el batch de eventos: {str(e)}", 500)
        finally:
            session.close()
