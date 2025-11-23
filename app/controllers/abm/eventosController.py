from flask import jsonify, request
from sqlalchemy.orm import joinedload
from app.backend.models import Evento, RegistroEvento, UsuarioxEvento, Usuario, IntentoReporte, EstadoReporte
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
                        "haFalladoEnElPasado": ux.haFalladoEnElPasado,
                        "esFallaGrave": ux.esFallaGrave
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
                    "dificultad": evento.dificultad,
                    "medio": evento.medio,
                    "registroEvento": {
                        "idRegistroEvento": evento.registroEvento.idRegistroEvento,
                        "asunto": evento.registroEvento.asunto,
                        "cuerpo": evento.registroEvento.cuerpo,
                        "objetivo": evento.registroEvento.objetivo,
                        "conversacion": evento.registroEvento.conversacion,
                        "remitente": evento.registroEvento.remitente
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
                    "haFalladoEnElPasado": ux.haFalladoEnElPasado,
                    "esFallaGrave": ux.esFallaGrave
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
                "dificultad": evento.dificultad,
                "medio": evento.medio,
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
                log.error("Tipo de evento no es valido")
                return responseError("TIPO_EVENTO_INVALIDO", "El tipo de evento no es válido", 400)

            fecha_evento_str = data.get("fechaEvento")
            if fecha_evento_str is None:
                fecha_evento = datetime.now()
            else:
                try:
                    fecha_evento = datetime.fromisoformat(fecha_evento_str)
                except ValueError:
                    log.error("Fecha no es valida")
                    return responseError("FECHA_INVALIDA", "El formato de la fecha no es válido", 400)

            session = SessionLocal()

            # Asignar dificultad aleatoria solo para MENSAJE y CORREO
            dificultad = None
            if tipo_evento_val in [TipoEvento.MENSAJE.value, TipoEvento.CORREO.value]:
                import random
                dificultades = ["Fácil", "Medio", "Difícil"]
                dificultad = random.choice(dificultades)

            nuevo_evento = Evento(
                tipoEvento=tipo_evento_val,
                fechaEvento=fecha_evento,
                dificultad=dificultad
            )

            if "registroEvento" in data:
                registro_evento_data = data["registroEvento"]
                if "asunto" in registro_evento_data or "cuerpo" in registro_evento_data or "objetivo" in registro_evento_data or "conversacion" in registro_evento_data or "remitente" in registro_evento_data:
                    nuevo_registro_evento = RegistroEvento(
                        asunto=registro_evento_data.get("asunto"),
                        cuerpo=registro_evento_data.get("cuerpo"),
                        objetivo=registro_evento_data.get("objetivo"),
                        conversacion=registro_evento_data.get("conversacion"),
                        remitente=registro_evento_data.get("remitente")
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
                if "objetivo" in registro_evento_data:
                    evento.registroEvento.objetivo = registro_evento_data["objetivo"]
                if "conversacion" in registro_evento_data:
                    evento.registroEvento.conversacion = registro_evento_data["conversacion"]
                if "remitente" in registro_evento_data:
                    evento.registroEvento.remitente = registro_evento_data["remitente"]

            session.commit()
            session.close()
            return jsonify({"mensaje": "Evento modificado correctamente"}), 200

        except Exception as e:
            session.close()
            return responseError("ERROR_MODIFICACION_EVENTO", f"Error al modificar el evento: {str(e)}", 500)


    @staticmethod
    def asociarUsuarioEvento(idEvento, idUsuario, resultado_val, fechaReporte=None, fechaFalla=None, esFallaGrave=None, haFalladoEnElPasado=None):
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
                # Actualizar esFallaGrave si se proporciona
                if esFallaGrave is not None:
                    usuario_evento.esFallaGrave = esFallaGrave
                # Actualizar haFalladoEnElPasado si se proporciona, o marcar automáticamente si el resultado es FALLA
                if haFalladoEnElPasado is not None:
                    usuario_evento.haFalladoEnElPasado = haFalladoEnElPasado
                elif ResultadoEvento(resultado_val) == ResultadoEvento.FALLA:
                    usuario_evento.haFalladoEnElPasado = True
            else:
                usuario_evento = UsuarioxEvento(
                    idEvento=idEvento,
                    idUsuario=idUsuario,
                    resultado=ResultadoEvento(resultado_val),
                    fechaReporte=fechaReporte,
                    fechaFalla=fechaFalla,
                    esFallaGrave=esFallaGrave if esFallaGrave is not None else False,
                    haFalladoEnElPasado=haFalladoEnElPasado if haFalladoEnElPasado is not None else (ResultadoEvento(resultado_val) == ResultadoEvento.FALLA)
                )
                session.add(usuario_evento)

            session.commit()
            session.close()
            return jsonify({"mensaje": "Usuario asociado al evento correctamente"}), 200

        except Exception as e:
            session.close()
            return responseError("ERROR_ASOCIAR_USUARIO_EVENTO", f"Error al asociar usuario al evento: {str(e)}", 500)


    @staticmethod
    def desasociarUsuarioEvento(idEvento, idUsuario):
        session = SessionLocal()
        try:
            usuario_evento = session.query(UsuarioxEvento).filter_by(
                idEvento=idEvento,
                idUsuario=idUsuario
            ).first()

            if not usuario_evento:
                return responseError("ASOCIACION_NO_ENCONTRADA", "No se encontró la asociación entre el usuario y el evento", 404)

            session.delete(usuario_evento)
            session.commit()
            session.close()
            return jsonify({"mensaje": "Usuario desasociado del evento correctamente"}), 200

        except Exception as e:
            session.rollback()
            session.close()
            return responseError("ERROR_DESASOCIAR_USUARIO_EVENTO", f"Error al desasociar usuario del evento: {str(e)}", 500)


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
                
                tipo_evento = TipoEvento(evento_data["tipoEvento"])
                
                # Asignar dificultad aleatoria solo para MENSAJE y CORREO
                dificultad = None
                if tipo_evento in [TipoEvento.MENSAJE, TipoEvento.CORREO]:
                    dificultades = ["Fácil", "Medio", "Difícil"]
                    dificultad = random.choice(dificultades)
                
                # Asignar medio aleatorio solo para MENSAJE
                medio = None
                if tipo_evento == TipoEvento.MENSAJE:
                    medios = ["whatsapp", "telegram", "sms"]
                    medio = random.choice(medios)
                
                # Crear evento
                evento = Evento(
                    tipoEvento=tipo_evento,
                    fechaEvento=datetime.fromisoformat(evento_data["fechaEvento"]),
                    dificultad=dificultad,
                    medio=medio
                )
                session.add(evento)
                session.flush()  # Para obtener el ID
                
                # Para eventos de tipo LLAMADA, generar remitente si no se proporciona
                remitente = evento_data.get("remitente")
                if tipo_evento == TipoEvento.LLAMADA and not remitente:
                    # Generar un remitente por defecto para eventos de llamada del batch
                    remitentes_default = [
                        "Juan Pérez", "María González", "Carlos Rodríguez", 
                        "Ana Martínez", "Luis Fernández", "Laura Sánchez"
                    ]
                    remitente = random.choice(remitentes_default)
                    log.info(f"Generando remitente por defecto para evento LLAMADA: {remitente}")
                
                # Crear registro del evento
                registro = RegistroEvento(
                    idEvento=evento.idEvento,
                    asunto=evento_data["asunto"],
                    cuerpo=evento_data.get("cuerpo"),
                    mensaje=evento_data.get("mensaje"),
                    remitente=remitente  # Para eventos de tipo LLAMADA
                )
                session.add(registro)
                
                # Obtener usuarios para este evento (si no se especifica, usar todos)
                usuarios_evento = evento_data.get("usuarios", usuarios_objetivo)
                
                # Crear resultados para usuarios
                for idUsuario in usuarios_evento:
                    # Determinar resultado basado en probabilidades o configuración
                    rand = random.random()
                    
                    # Variable para determinar si es falla grave (50% de probabilidad cuando hay falla)
                    esFallaGrave = False
                    
                    # Usuarios 7, 8, 9 tienen más probabilidad de reportar eventos
                    if idUsuario in [7, 8, 9]:
                        if rand < 0.1:  # 10% falla activa
                            resultado = ResultadoEvento.FALLA
                            fechaFalla = evento.fechaEvento + timedelta(minutes=random.randint(5, 60))
                            fechaReporte = None
                            haFalladoEnElPasado = True
                            # 50% de probabilidad de que sea falla grave
                            esFallaGrave = random.random() < 0.5
                        elif rand < 0.3:  # 20% reportado con falla previa
                            resultado = ResultadoEvento.REPORTADO
                            fechaFalla = evento.fechaEvento + timedelta(minutes=random.randint(5, 30))
                            fechaReporte = evento.fechaEvento + timedelta(minutes=random.randint(10, 120))
                            haFalladoEnElPasado = True
                            # 50% de probabilidad de que la falla previa haya sido grave
                            esFallaGrave = random.random() < 0.5
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
                            # 50% de probabilidad de que sea falla grave
                            esFallaGrave = random.random() < 0.5
                        elif rand < 0.6:  # 20% reportado (falla pasada)
                            resultado = ResultadoEvento.REPORTADO
                            fechaFalla = evento.fechaEvento + timedelta(minutes=random.randint(5, 30))
                            fechaReporte = evento.fechaEvento + timedelta(minutes=random.randint(10, 120))
                            haFalladoEnElPasado = True
                            # 50% de probabilidad de que la falla previa haya sido grave
                            esFallaGrave = random.random() < 0.5
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
                        haFalladoEnElPasado=haFalladoEnElPasado,
                        esFallaGrave=esFallaGrave
                    )
                    session.add(usuario_evento)
                    
                    resultados_creados.append({
                        "idUsuario": idUsuario,
                        "idEvento": evento.idEvento,
                        "resultado": resultado.value,
                        "fechaFalla": fechaFalla.isoformat() if fechaFalla else None,
                        "fechaReporte": fechaReporte.isoformat() if fechaReporte else None,
                        "haFalladoEnElPasado": haFalladoEnElPasado,
                        "esFallaGrave": esFallaGrave
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
                    "fallas_activas_simples": len([r for r in resultados_creados if r["resultado"] == "FALLA" and not r.get("esFallaGrave", False)]),
                    "fallas_activas_graves": len([r for r in resultados_creados if r["resultado"] == "FALLA" and r.get("esFallaGrave", False)]),
                    "reportados": len([r for r in resultados_creados if r["resultado"] == "REPORTADO"]),
                    "fallas_pasadas": len([r for r in resultados_creados if r["haFalladoEnElPasado"] and r["resultado"] != "FALLA"]),
                    "fallas_pasadas_simples": len([r for r in resultados_creados if r["haFalladoEnElPasado"] and r["resultado"] != "FALLA" and not r.get("esFallaGrave", False)]),
                    "fallas_pasadas_graves": len([r for r in resultados_creados if r["haFalladoEnElPasado"] and r["resultado"] != "FALLA" and r.get("esFallaGrave", False)]),
                    "pendientes": len([r for r in resultados_creados if r["resultado"] == "PENDIENTE" and not r["haFalladoEnElPasado"]])
                }
            }), 200
            
        except Exception as e:
            session.rollback()
            log.error(f"Error creando batch de eventos: {str(e)}")
            return responseError("ERROR", f"No se pudo crear el batch de eventos: {str(e)}", 500)
        finally:
            session.close()

    @staticmethod
    def obtenerIntentosReporte():
        """
        Obtiene todos los intentos de reporte con información del usuario
        """
        session = SessionLocal()
        try:
            intentos = session.query(IntentoReporte).options(
                joinedload(IntentoReporte.usuario),
                joinedload(IntentoReporte.eventoVerificado)
            ).order_by(IntentoReporte.fechaIntento.desc()).all()

            intentos_data = []
            for intento in intentos:
                intento_info = {
                    "idIntentoReporte": intento.idIntentoReporte,
                    "idUsuario": intento.idUsuario,
                    "nombreUsuario": f"{intento.usuario.nombre} {intento.usuario.apellido}" if intento.usuario else "N/A",
                    "tipoEvento": intento.tipoEvento,
                    "fechaInicio": intento.fechaInicio.isoformat() if intento.fechaInicio else None,
                    "fechaFin": intento.fechaFin.isoformat() if intento.fechaFin else None,
                    "fechaIntento": intento.fechaIntento.isoformat() if intento.fechaIntento else None,
                    "verificado": intento.verificado,
                    "resultadoVerificacion": intento.resultadoVerificacion,
                    "idEventoVerificado": intento.idEventoVerificado,
                    "observaciones": intento.observaciones,
                    "estado": intento.estado.value if intento.estado else EstadoReporte.PENDIENTE.value
                }
                intentos_data.append(intento_info)

            return jsonify({"intentos": intentos_data}), 200
        except Exception as e:
            log.error(f"Error obteniendo intentos de reporte: {str(e)}")
            return responseError("ERROR", f"Error al obtener intentos de reporte: {str(e)}", 500)
        finally:
            session.close()

    @staticmethod
    def actualizarIntentoReporte(idIntentoReporte, data):
        """
        Actualiza un intento de reporte (observaciones, estado, etc.)
        """
        session = SessionLocal()
        try:
            intento = session.query(IntentoReporte).filter_by(idIntentoReporte=idIntentoReporte).first()
            
            if not intento:
                return responseError("INTENTO_NO_ENCONTRADO", "No se encontró el intento de reporte", 404)

            # Guardar el estado anterior para detectar cambios
            estado_anterior = intento.estado
            id_evento_anterior = intento.idEventoVerificado

            # Actualizar campos permitidos
            if "observaciones" in data:
                intento.observaciones = data["observaciones"]
            
            if "estado" in data:
                estado_val = data["estado"]
                if estado_val not in [e.value for e in EstadoReporte]:
                    return responseError("ESTADO_INVALIDO", "El estado proporcionado no es válido", 400)
                intento.estado = EstadoReporte(estado_val)
            
            if "verificado" in data:
                intento.verificado = data["verificado"]
            
            if "resultadoVerificacion" in data:
                intento.resultadoVerificacion = data["resultadoVerificacion"]
            
            if "idEventoVerificado" in data:
                intento.idEventoVerificado = data["idEventoVerificado"]

            # Si se cambió de VERIFICADO a otro estado, revertir el estado REPORTADO del evento
            if estado_anterior == EstadoReporte.VERIFICADO and intento.estado != EstadoReporte.VERIFICADO:
                if id_evento_anterior:
                    usuario_evento = session.query(UsuarioxEvento).filter_by(
                        idUsuario=intento.idUsuario,
                        idEvento=id_evento_anterior
                    ).first()
                    
                    if usuario_evento and usuario_evento.resultado == ResultadoEvento.REPORTADO:
                        # Revertir a PENDIENTE
                        usuario_evento.resultado = ResultadoEvento.PENDIENTE
                        usuario_evento.fechaReporte = None
                        log.info(f"Revertido estado REPORTADO del evento {id_evento_anterior} para usuario {intento.idUsuario}")

            session.commit()
            log.info(f"Intento de reporte {idIntentoReporte} actualizado correctamente")
            return jsonify({"mensaje": "Intento de reporte actualizado correctamente"}), 200

        except Exception as e:
            session.rollback()
            log.error(f"Error actualizando intento de reporte: {str(e)}")
            return responseError("ERROR", f"Error al actualizar intento de reporte: {str(e)}", 500)
        finally:
            session.close()

    @staticmethod
    def validarIntentoReporte(idIntentoReporte, observaciones=None):
        """
        Valida un intento de reporte sin asignar evento (cuando no hay evento correspondiente)
        """
        session = SessionLocal()
        try:
            intento = session.query(IntentoReporte).filter_by(idIntentoReporte=idIntentoReporte).first()
            
            if not intento:
                return responseError("INTENTO_NO_ENCONTRADO", "No se encontró el intento de reporte", 404)

            intento.estado = EstadoReporte.VALIDADO_SIN_EVENTO
            intento.verificado = True
            intento.resultadoVerificacion = "Validado por el administrador sin evento asociado"
            
            if observaciones:
                intento.observaciones = observaciones

            session.commit()
            log.info(f"Intento de reporte {idIntentoReporte} validado sin evento")
            return jsonify({"mensaje": "Intento validado correctamente"}), 200

        except Exception as e:
            session.rollback()
            log.error(f"Error validando intento de reporte: {str(e)}")
            return responseError("ERROR", f"Error al validar intento de reporte: {str(e)}", 500)
        finally:
            session.close()

    @staticmethod
    def rechazarIntentoReporte(idIntentoReporte, observaciones=None):
        """
        Rechaza/descarta un intento de reporte
        """
        session = SessionLocal()
        try:
            intento = session.query(IntentoReporte).filter_by(idIntentoReporte=idIntentoReporte).first()
            
            if not intento:
                return responseError("INTENTO_NO_ENCONTRADO", "No se encontró el intento de reporte", 404)

            intento.estado = EstadoReporte.RECHAZADO
            intento.verificado = False
            intento.resultadoVerificacion = "Rechazado por el administrador"
            
            if observaciones:
                intento.observaciones = observaciones

            session.commit()
            log.info(f"Intento de reporte {idIntentoReporte} rechazado")
            return jsonify({"mensaje": "Intento rechazado correctamente"}), 200

        except Exception as e:
            session.rollback()
            log.error(f"Error rechazando intento de reporte: {str(e)}")
            return responseError("ERROR", f"Error al rechazar intento de reporte: {str(e)}", 500)
        finally:
            session.close()

    @staticmethod
    def verificarIntentoReporte(idIntentoReporte, idEvento, observaciones=None):
        """
        Verifica un intento de reporte asociándolo a un evento existente
        """
        session = SessionLocal()
        try:
            intento = session.query(IntentoReporte).filter_by(idIntentoReporte=idIntentoReporte).first()
            
            if not intento:
                return responseError("INTENTO_NO_ENCONTRADO", "No se encontró el intento de reporte", 404)

            # Verificar que el evento existe
            evento = session.query(Evento).filter_by(idEvento=idEvento).first()
            if not evento:
                return responseError("EVENTO_NO_ENCONTRADO", "No se encontró el evento especificado", 404)

            intento.estado = EstadoReporte.VERIFICADO
            intento.verificado = True
            intento.idEventoVerificado = idEvento
            intento.resultadoVerificacion = f"Verificado y asociado al evento #{idEvento}"
            
            if observaciones:
                intento.observaciones = observaciones

            session.commit()
            log.info(f"Intento de reporte {idIntentoReporte} verificado con evento {idEvento}")
            return jsonify({"mensaje": "Intento verificado correctamente"}), 200

        except Exception as e:
            session.rollback()
            log.error(f"Error verificando intento de reporte: {str(e)}")
            return responseError("ERROR", f"Error al verificar intento de reporte: {str(e)}", 500)
        finally:
            session.close()

    @staticmethod
    def eliminarIntentoReporte(idIntentoReporte):
        """
        Elimina un intento de reporte
        """
        session = SessionLocal()
        try:
            intento = session.query(IntentoReporte).filter_by(idIntentoReporte=idIntentoReporte).first()
            
            if not intento:
                return responseError("INTENTO_NO_ENCONTRADO", "No se encontró el intento de reporte", 404)

            session.delete(intento)
            session.commit()
            log.info(f"Intento de reporte {idIntentoReporte} eliminado")
            return jsonify({"mensaje": "Intento eliminado correctamente"}), 200

        except Exception as e:
            session.rollback()
            log.error(f"Error eliminando intento de reporte: {str(e)}")
            return responseError("ERROR", f"Error al eliminar intento de reporte: {str(e)}", 500)
        finally:
            session.close()
