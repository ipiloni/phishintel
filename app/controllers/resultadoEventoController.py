from flask import jsonify
from datetime import datetime, timedelta
from app.backend.models.error import responseError
from app.backend.models.resultadoEvento import ResultadoEvento
from app.backend.models.usuarioxevento import UsuarioxEvento
from app.backend.models.tipoEvento import TipoEvento
from app.backend.models.intentoReporte import IntentoReporte
from app.backend.models.evento import Evento
from app.config.db_config import SessionLocal
from app.utils.logger import log

# Variable global para contar fallas
conteo_fallas = {"total": 0}

# Puntos de falla simple (se RESTAN del puntaje inicial de 100)
PUNTOS_FALLA_SIMPLE = 5

# Puntos de falla grave (se RESTAN del puntaje inicial de 100)
PUNTOS_FALLA_GRAVE = 20

# Puntos por evento reportado (se SUMAN al puntaje)
PUNTOS_REPORTADO = 5

# Puntaje inicial para todos los empleados
PUNTAJE_INICIAL = 100

class ResultadoEventoController:

    @staticmethod
    def sumarFalla(idUsuario, idEvento, fechaFalla=None, esFallaGrave=False):
        log.info(f"[SUMAR_FALLA] Iniciando - idUsuario: {idUsuario}, idEvento: {idEvento}, fechaFalla: {fechaFalla}, esFallaGrave: {esFallaGrave}")
        session = SessionLocal()
        try:
            # Buscar relación usuario-evento
            usuario_evento = session.query(UsuarioxEvento).filter_by(
                idUsuario=idUsuario,
                idEvento=idEvento
            ).first()

            if not usuario_evento:
                log.error(f"[SUMAR_FALLA] ERROR - No existe relación Usuario {idUsuario} - Evento {idEvento}")
                session.close()
                # Verificar si estamos en contexto de aplicación
                try:
                    from flask import current_app
                    current_app._get_current_object()
                    return responseError("RELACION_NO_ENCONTRADA", "No existe relación entre el usuario y el evento", 404)
                except RuntimeError:
                    log.error(f"[SUMAR_FALLA] Error sin contexto de aplicación: No existe relación")
                    return None

            log.info(f"[SUMAR_FALLA] Relación encontrada - Estado anterior: resultado={usuario_evento.resultado.value}, esFallaGrave={usuario_evento.esFallaGrave}")

            # Actualizar a FALLA
            usuario_evento.resultado = ResultadoEvento.FALLA
            # Si no se proporciona fecha, usar la fecha actual
            if fechaFalla is None:
                fechaFalla = datetime.now()
            usuario_evento.fechaFalla = fechaFalla
            # Marcar si es falla grave
            usuario_evento.esFallaGrave = esFallaGrave
            # Marcar que ha fallado en el pasado
            usuario_evento.haFalladoEnElPasado = True
            
            log.info(f"[SUMAR_FALLA] Antes de commit - resultado={usuario_evento.resultado.value}, esFallaGrave={usuario_evento.esFallaGrave}, fechaFalla={usuario_evento.fechaFalla}")
            session.commit()
            log.info(f"[SUMAR_FALLA] Commit exitoso - Falla registrada correctamente")
            session.close()

            # Verificar si estamos en un contexto de aplicación Flask
            try:
                from flask import current_app
                current_app._get_current_object()
                # Si llegamos aquí, hay contexto de aplicación, usar jsonify
                return jsonify({
                    "mensaje": "Falla registrada", 
                    "idUsuario": idUsuario, 
                    "idEvento": idEvento,
                    "fechaFalla": fechaFalla.isoformat(),
                    "esFallaGrave": esFallaGrave
                }), 200
            except RuntimeError:
                # No hay contexto de aplicación (probablemente llamado desde un hilo)
                # Retornar diccionario en lugar de Response
                log.info(f"[SUMAR_FALLA] Retornando diccionario (sin contexto de aplicación)")
                return {
                    "mensaje": "Falla registrada", 
                    "idUsuario": idUsuario, 
                    "idEvento": idEvento,
                    "fechaFalla": fechaFalla.isoformat(),
                    "esFallaGrave": esFallaGrave
                }

        except Exception as e:
            log.error(f"[SUMAR_FALLA] ERROR - Excepción al intentar sumar la falla: {str(e)}", exc_info=True)
            session.rollback()
            session.close()
            # Verificar si estamos en contexto de aplicación para retornar responseError
            try:
                from flask import current_app
                current_app._get_current_object()
                return responseError("ERROR", f"No se pudo registrar la falla: {str(e)}", 500)
            except RuntimeError:
                # Sin contexto, solo loguear el error
                log.error(f"[SUMAR_FALLA] Error sin contexto de aplicación: {str(e)}")
                return None

    @staticmethod
    def sumarFallaGrave(idUsuario, idEvento, fechaFalla=None):
        """
        Registra una falla grave. Actualiza el campo esFallaGrave a True.
        Si el evento aún no está marcado como FALLA, también lo marca como tal.
        """
        log.info(f"[SUMAR_FALLA_GRAVE] Iniciando - idUsuario: {idUsuario}, idEvento: {idEvento}, fechaFalla: {fechaFalla}")
        session = SessionLocal()
        try:
            # Buscar relación usuario-evento
            usuario_evento = session.query(UsuarioxEvento).filter_by(
                idUsuario=idUsuario,
                idEvento=idEvento
            ).first()

            if not usuario_evento:
                log.error(f"[SUMAR_FALLA_GRAVE] ERROR - No existe relación Usuario {idUsuario} - Evento {idEvento}")
                session.close()
                return responseError("RELACION_NO_ENCONTRADA", "No existe relación entre el usuario y el evento", 404)

            log.info(f"[SUMAR_FALLA_GRAVE] Relación encontrada - Estado anterior: resultado={usuario_evento.resultado.value}, esFallaGrave={usuario_evento.esFallaGrave}")

            # Actualizar a FALLA si no lo está ya
            usuario_evento.resultado = ResultadoEvento.FALLA
            # Si no se proporciona fecha, usar la fecha actual
            if fechaFalla is None:
                fechaFalla = datetime.now()
            usuario_evento.fechaFalla = fechaFalla
            # Marcar como falla grave
            usuario_evento.esFallaGrave = True
            # Marcar que ha fallado en el pasado
            usuario_evento.haFalladoEnElPasado = True
            
            log.info(f"[SUMAR_FALLA_GRAVE] Antes de commit - resultado={usuario_evento.resultado.value}, esFallaGrave={usuario_evento.esFallaGrave}, fechaFalla={usuario_evento.fechaFalla}")
            session.commit()
            log.info(f"[SUMAR_FALLA_GRAVE] Commit exitoso - Falla grave registrada correctamente")

            return jsonify({
                "mensaje": "Falla grave registrada", 
                "idUsuario": idUsuario, 
                "idEvento": idEvento,
                "fechaFalla": fechaFalla.isoformat(),
                "esFallaGrave": True
            }), 200

        except Exception as e:
            log.error(f"[SUMAR_FALLA_GRAVE] ERROR - Excepción al intentar sumar la falla grave: {str(e)}", exc_info=True)
            session.rollback()
            return responseError("ERROR", f"No se pudo registrar la falla grave: {str(e)}", 500)
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
                "fechaReporte": fechaReporte.isoformat(),
                "puntos_ganados": PUNTOS_REPORTADO
            }), 200

        except Exception as e:
            log.error("Hubo un error al intentar sumar el reporte: " + str(e))
            session.rollback()
            return responseError("ERROR", f"No se pudo registrar el reporte: {str(e)}", 500)
        finally:
            session.close()

    @staticmethod
    def calcularScoringPorEmpleado(idUsuario):
        """
        Calcula el scoring individual de un empleado específico.
        Sistema invertido: empieza con 100 puntos y va perdiendo por fallas.
        """
        session = SessionLocal()
        try:
            from app.backend.models.usuario import Usuario
            from app.backend.models.evento import Evento
            from sqlalchemy import func

            # Obtener datos del empleado
            empleado = session.query(Usuario).filter_by(idUsuario=idUsuario).first()
            if not empleado:
                return responseError("USUARIO_NO_ENCONTRADO", "Usuario no encontrado", 404)

            # Obtener fallas del empleado con información de esFallaGrave
            fallas_query = (
                session.query(UsuarioxEvento)
                .filter(UsuarioxEvento.idUsuario == idUsuario)
                .filter(UsuarioxEvento.resultado == ResultadoEvento.FALLA)
                .all()
            )

            # Obtener eventos reportados del empleado
            reportados = (
                session.query(
                    func.count(UsuarioxEvento.idEvento).label("cantidad_reportados")
                )
                .filter(UsuarioxEvento.idUsuario == idUsuario)
                .filter(UsuarioxEvento.resultado == ResultadoEvento.REPORTADO)
                .scalar()
            ) or 0

            # Calcular puntos perdidos por fallas (basado en esFallaGrave)
            puntos_perdidos = 0
            total_fallas = 0
            total_fallas_simples = 0
            total_fallas_graves = 0
            desglose_por_tipo = {
                "fallas_simples": {
                    "cantidad": 0,
                    "puntos_perdidos": 0
                },
                "fallas_graves": {
                    "cantidad": 0,
                    "puntos_perdidos": 0
                }
            }

            for usuario_evento in fallas_query:
                total_fallas += 1
                if usuario_evento.esFallaGrave:
                    puntos_perdidos += PUNTOS_FALLA_GRAVE
                    total_fallas_graves += 1
                    desglose_por_tipo["fallas_graves"]["cantidad"] += 1
                    desglose_por_tipo["fallas_graves"]["puntos_perdidos"] += PUNTOS_FALLA_GRAVE
                else:
                    puntos_perdidos += PUNTOS_FALLA_SIMPLE
                    total_fallas_simples += 1
                    desglose_por_tipo["fallas_simples"]["cantidad"] += 1
                    desglose_por_tipo["fallas_simples"]["puntos_perdidos"] += PUNTOS_FALLA_SIMPLE

            # Calcular puntos ganados por reportes
            puntos_ganados = int(reportados) * PUNTOS_REPORTADO

            # Calcular penalización por fallas en el pasado (basado en esFallaGrave)
            penalizacion_falla_pasado = 0
            ha_fallado_en_pasado = False
            
            # Obtener fallas del pasado (incluyendo las que fueron reportadas después)
            fallas_pasado = (
                session.query(UsuarioxEvento)
                .filter(UsuarioxEvento.idUsuario == idUsuario)
                .filter(UsuarioxEvento.haFalladoEnElPasado == True)
                .filter(UsuarioxEvento.resultado != ResultadoEvento.FALLA)  # Excluir solo fallas activas
                .all()
            )
            
            # Calcular penalización total por fallas en el pasado
            for usuario_evento in fallas_pasado:
                if usuario_evento.esFallaGrave:
                    penalizacion_falla_pasado += PUNTOS_FALLA_GRAVE
                else:
                    penalizacion_falla_pasado += PUNTOS_FALLA_SIMPLE
                ha_fallado_en_pasado = True

            # Calcular puntos restantes (100 - puntos_perdidos - penalizacion_falla_pasado + puntos_ganados)
            puntos_restantes = max(0, PUNTAJE_INICIAL - puntos_perdidos - penalizacion_falla_pasado + puntos_ganados)

            # Determinar nivel de riesgo basado en puntos restantes
            nivel_riesgo = ResultadoEventoController._determinarNivelRiesgo(puntos_restantes)

            # Función auxiliar para obtener el título del evento
            def obtener_titulo_evento(evento, registro):
                """Obtiene el título del evento. Para MENSAJE, muestra los primeros 40 caracteres del mensaje. Para LLAMADA, muestra el remitente."""
                if not registro:
                    return f"Evento {evento.tipoEvento.value}"
                
                # Para eventos de tipo LLAMADA, mostrar el remitente
                if evento.tipoEvento == TipoEvento.LLAMADA:
                    if registro.remitente:
                        return f"Llamada de {registro.remitente}"
                    else:
                        return f"Evento {evento.tipoEvento.value}"
                
                # Para eventos de tipo MENSAJE, usar el contenido del mensaje
                if evento.tipoEvento == TipoEvento.MENSAJE:
                    # El mensaje puede estar en registro.mensaje o registro.cuerpo
                    mensaje_texto = None
                    if registro.mensaje:
                        mensaje_texto = registro.mensaje.strip()
                    elif registro.cuerpo:
                        mensaje_texto = registro.cuerpo.strip()
                    
                    if mensaje_texto:
                        # Limpiar saltos de línea y espacios múltiples
                        mensaje_texto = ' '.join(mensaje_texto.split())
                        # Remover HTML tags si existen
                        import re
                        mensaje_texto = re.sub(r'<[^>]+>', '', mensaje_texto)
                        # Tomar primeros 40 caracteres y agregar ... si es más largo
                        preview = mensaje_texto[:40] + ('...' if len(mensaje_texto) > 40 else '')
                        return preview
                    elif registro.asunto:
                        return registro.asunto
                    else:
                        return f"Evento {evento.tipoEvento.value}"
                else:
                    # Para otros tipos de evento, usar el asunto
                    return registro.asunto if registro.asunto else f"Evento {evento.tipoEvento.value}"

            # Obtener eventos específicos para el desglose detallado
            from app.backend.models.registroEvento import RegistroEvento
            
            # 1. Fallas activas (sin reportar) - incluir UsuarioxEvento para obtener esFallaGrave
            eventos_activos = (
                session.query(Evento, RegistroEvento, UsuarioxEvento)
                .join(UsuarioxEvento, UsuarioxEvento.idEvento == Evento.idEvento)
                .outerjoin(RegistroEvento, RegistroEvento.idEvento == Evento.idEvento)
                .filter(UsuarioxEvento.idUsuario == idUsuario)
                .filter(UsuarioxEvento.resultado == ResultadoEvento.FALLA)
                .all()
            )
            
            # 2. Eventos reportados (incluyendo los que fueron fallados y luego reportados)
            eventos_reportados = (
                session.query(Evento, RegistroEvento, UsuarioxEvento)
                .join(UsuarioxEvento, UsuarioxEvento.idEvento == Evento.idEvento)
                .outerjoin(RegistroEvento, RegistroEvento.idEvento == Evento.idEvento)
                .filter(UsuarioxEvento.idUsuario == idUsuario)
                .filter(UsuarioxEvento.resultado == ResultadoEvento.REPORTADO)
                .all()
            )
            
            # 3. Eventos pendientes (sin falla ni reporte)
            eventos_pendientes = (
                session.query(Evento, RegistroEvento, UsuarioxEvento)
                .join(UsuarioxEvento, UsuarioxEvento.idEvento == Evento.idEvento)
                .outerjoin(RegistroEvento, RegistroEvento.idEvento == Evento.idEvento)
                .filter(UsuarioxEvento.idUsuario == idUsuario)
                .filter(UsuarioxEvento.resultado == ResultadoEvento.PENDIENTE)
                .all()
            )

            return jsonify({
                "idUsuario": empleado.idUsuario,
                "nombre": empleado.nombre,
                "apellido": empleado.apellido,
                "puntos_restantes": puntos_restantes,
                "puntos_perdidos": puntos_perdidos,
                "puntos_ganados": puntos_ganados,
                "penalizacion_falla_pasado": penalizacion_falla_pasado,
                "ha_fallado_en_pasado": bool(ha_fallado_en_pasado),
                "puntaje_inicial": PUNTAJE_INICIAL,
                "total_fallas": total_fallas,
                "total_reportados": int(reportados),
                "nivel_riesgo": nivel_riesgo,
                "desglose_por_tipo": desglose_por_tipo,
                "eventos_detalle": {
                    "activos": [
                        {
                            "idEvento": evento.idEvento,
                            "titulo": obtener_titulo_evento(evento, registro),
                            "tipoEvento": evento.tipoEvento.value,
                            "fechaCreacion": evento.fechaEvento.isoformat() if evento.fechaEvento else None,
                            "fechaFalla": usuario_evento.fechaFalla.isoformat() if usuario_evento.fechaFalla else None,
                            "puntos": PUNTOS_FALLA_GRAVE if usuario_evento.esFallaGrave else PUNTOS_FALLA_SIMPLE,
                            "esFallaGrave": usuario_evento.esFallaGrave,
                            "dificultad": evento.dificultad if evento.tipoEvento in [TipoEvento.MENSAJE, TipoEvento.CORREO] else None,
                            "medio": evento.medio if evento.tipoEvento == TipoEvento.MENSAJE else None,
                            "tipo": "falla_activa"
                        } for evento, registro, usuario_evento in eventos_activos
                    ],
                    "reportados": [
                        {
                            "idEvento": evento.idEvento,
                            "titulo": obtener_titulo_evento(evento, registro),
                            "tipoEvento": evento.tipoEvento.value,
                            "fechaCreacion": evento.fechaEvento.isoformat() if evento.fechaEvento else None,
                            "puntos": PUNTOS_REPORTADO,
                            "haFalladoEnElPasado": usuario_evento.haFalladoEnElPasado,
                            "puntosFallaPasada": (PUNTOS_FALLA_GRAVE if usuario_evento.esFallaGrave else PUNTOS_FALLA_SIMPLE) if usuario_evento.haFalladoEnElPasado else 0,
                            "esFallaGrave": usuario_evento.esFallaGrave if usuario_evento.haFalladoEnElPasado else False,
                            "dificultad": evento.dificultad if evento.tipoEvento in [TipoEvento.MENSAJE, TipoEvento.CORREO] else None,
                            "medio": evento.medio if evento.tipoEvento == TipoEvento.MENSAJE else None,
                            "tipo": "falla_reportada" if usuario_evento.haFalladoEnElPasado else "reportado"
                        } for evento, registro, usuario_evento in eventos_reportados
                    ],
                    "pendientes": [
                        {
                            "idEvento": evento.idEvento,
                            "titulo": obtener_titulo_evento(evento, registro),
                            "tipoEvento": evento.tipoEvento.value,
                            "fechaCreacion": evento.fechaEvento.isoformat() if evento.fechaEvento else None,
                            "puntos": 0,
                            "dificultad": evento.dificultad if evento.tipoEvento in [TipoEvento.MENSAJE, TipoEvento.CORREO] else None,
                            "medio": evento.medio if evento.tipoEvento == TipoEvento.MENSAJE else None,
                            "tipo": "pendiente"
                        } for evento, registro, usuario_evento in eventos_pendientes
                    ]
                }
            }), 200

        except Exception as e:
            log.error(f"Error calculando scoring por empleado: {str(e)}")
            return responseError("ERROR", f"No se pudo calcular el scoring: {str(e)}", 500)
        finally:
            session.close()

    @staticmethod
    def obtenerFallasPorEmpleadoConScoring(tipos_evento=None):
        """
        Obtiene TODOS los empleados con scoring y niveles de riesgo, incluyendo los que no tienen fallas.
        """
        session = SessionLocal()
        try:
            from app.backend.models.usuario import Usuario
            from app.backend.models.area import Area
            from app.backend.models.evento import Evento
            from sqlalchemy import func, and_
            
            # Primero obtener TODOS los empleados por área
            todos_empleados = (
                session.query(
                    Area.idArea,
                    Area.nombreArea,
                    Usuario.idUsuario,
                    Usuario.nombre,
                    Usuario.apellido
                )
                .join(Usuario, Usuario.idArea == Area.idArea)
                .all()
            )
            
            # Crear diccionario con todos los empleados
            empleados_dict = {}
            for emp in todos_empleados:
                empleado_key = f"{emp.idArea}_{emp.idUsuario}"
                empleados_dict[empleado_key] = {
                    'idArea': emp.idArea,
                    'nombreArea': emp.nombreArea,
                    'idUsuario': emp.idUsuario,
                    'nombre': emp.nombre,
                    'apellido': emp.apellido,
                    'puntos_restantes': PUNTAJE_INICIAL,  # Empiezan con 100 puntos
                    'puntos_perdidos': 0,
                    'puntos_ganados': 0,
                    'penalizacion_falla_pasado': 0,
                    'ha_fallado_en_pasado': False,
                    'total_fallas': 0,
                    'total_reportados': 0,
                    'total_eventos': 0,
                    'fallas_por_tipo': {}
                }
            
            # Ahora obtener las fallas de los empleados agrupadas por tipo de evento (con información de esFallaGrave)
            query_fallas = (
                session.query(
                    Area.idArea,
                    Area.nombreArea,
                    Usuario.idUsuario,
                    Usuario.nombre,
                    Usuario.apellido,
                    Evento.tipoEvento,
                    UsuarioxEvento.esFallaGrave,
                    func.count(UsuarioxEvento.idEvento).label("cantidad")
                )
                .join(Usuario, Usuario.idArea == Area.idArea)
                .join(UsuarioxEvento, UsuarioxEvento.idUsuario == Usuario.idUsuario)
                .join(Evento, Evento.idEvento == UsuarioxEvento.idEvento)
                .filter(UsuarioxEvento.resultado == ResultadoEvento.FALLA)
                .group_by(Area.idArea, Area.nombreArea, Usuario.idUsuario, Usuario.nombre, Usuario.apellido, Evento.tipoEvento, UsuarioxEvento.esFallaGrave)
            )
            
            # Obtener eventos reportados por empleado
            query_reportados = (
                session.query(
                    Area.idArea,
                    Usuario.idUsuario,
                    func.count(UsuarioxEvento.idEvento).label("cantidad_reportados")
                )
                .join(Usuario, Usuario.idArea == Area.idArea)
                .join(UsuarioxEvento, UsuarioxEvento.idUsuario == Usuario.idUsuario)
                .filter(UsuarioxEvento.resultado == ResultadoEvento.REPORTADO)
                .group_by(Area.idArea, Usuario.idUsuario)
                .all()
            )
            
            # Aplicar filtro por tipos de evento si se especifica
            if tipos_evento and len(tipos_evento) > 0:
                query_fallas = query_fallas.filter(Evento.tipoEvento.in_(tipos_evento))
            
            resultados_fallas = query_fallas.all()
            
            # Procesar las fallas y actualizar el diccionario de empleados
            for r in resultados_fallas:
                empleado_key = f"{r.idArea}_{r.idUsuario}"
                
                if empleado_key in empleados_dict:
                    empleado = empleados_dict[empleado_key]
                    cantidad = int(r.cantidad)
                    
                    if r.esFallaGrave:
                        puntos_perdidos = cantidad * PUNTOS_FALLA_GRAVE
                    else:
                        puntos_perdidos = cantidad * PUNTOS_FALLA_SIMPLE
                    
                    empleado['puntos_perdidos'] += puntos_perdidos
                    empleado['total_fallas'] += cantidad
                    
                    # Agrupar por tipo de evento con información de simples/graves
                    tipo_evento_key = r.tipoEvento.value
                    if tipo_evento_key not in empleado['fallas_por_tipo']:
                        empleado['fallas_por_tipo'][tipo_evento_key] = {
                            'cantidad': 0,
                            'simples': 0,
                            'graves': 0,
                            'puntos_perdidos': 0
                        }
                    
                    empleado['fallas_por_tipo'][tipo_evento_key]['cantidad'] += cantidad
                    if r.esFallaGrave:
                        empleado['fallas_por_tipo'][tipo_evento_key]['graves'] += cantidad
                    else:
                        empleado['fallas_por_tipo'][tipo_evento_key]['simples'] += cantidad
                    empleado['fallas_por_tipo'][tipo_evento_key]['puntos_perdidos'] += puntos_perdidos
            
            # Procesar eventos reportados y actualizar el diccionario de empleados
            for r in query_reportados:
                empleado_key = f"{r.idArea}_{r.idUsuario}"
                
                if empleado_key in empleados_dict:
                    empleado = empleados_dict[empleado_key]
                    cantidad_reportados = int(r.cantidad_reportados)
                    puntos_ganados = cantidad_reportados * PUNTOS_REPORTADO
                    
                    empleado['puntos_ganados'] = puntos_ganados
                    empleado['total_reportados'] = cantidad_reportados
            
            # Obtener fallas del pasado para todos los empleados (incluyendo las que fueron reportadas después)
            query_falla_pasado = (
                session.query(
                    Area.idArea,
                    Usuario.idUsuario,
                    UsuarioxEvento.esFallaGrave
                )
                .join(Usuario, Usuario.idArea == Area.idArea)
                .join(UsuarioxEvento, UsuarioxEvento.idUsuario == Usuario.idUsuario)
                .filter(UsuarioxEvento.haFalladoEnElPasado == True)
                .filter(UsuarioxEvento.resultado != ResultadoEvento.FALLA)  # Excluir solo fallas activas
                .all()
            )
            
            # Procesar fallas del pasado (basado en esFallaGrave)
            for r in query_falla_pasado:
                empleado_key = f"{r.idArea}_{r.idUsuario}"
                if empleado_key in empleados_dict:
                    if r.esFallaGrave:
                        penalizacion = PUNTOS_FALLA_GRAVE
                    else:
                        penalizacion = PUNTOS_FALLA_SIMPLE
                    
                    empleados_dict[empleado_key]['ha_fallado_en_pasado'] = True
                    empleados_dict[empleado_key]['penalizacion_falla_pasado'] += penalizacion
            
            # Obtener total de eventos por empleado
            query_eventos = (
                session.query(
                    Area.idArea,
                    Usuario.idUsuario,
                    func.count(UsuarioxEvento.idEvento).label("total_eventos")
                )
                .join(Usuario, Usuario.idArea == Area.idArea)
                .join(UsuarioxEvento, UsuarioxEvento.idUsuario == Usuario.idUsuario)
                .group_by(Area.idArea, Usuario.idUsuario)
                .all()
            )
            
            # Procesar eventos por empleado
            for r in query_eventos:
                empleado_key = f"{r.idArea}_{r.idUsuario}"
                if empleado_key in empleados_dict:
                    empleados_dict[empleado_key]['total_eventos'] = int(r.total_eventos)
            
            # Asegurar que todos los empleados tengan puntos_restantes calculados correctamente
            for empleado in empleados_dict.values():
                # Calcular puntos restantes: 100 - puntos perdidos - penalizacion_falla_pasado + puntos ganados
                empleado['puntos_restantes'] = max(0, PUNTAJE_INICIAL - empleado['puntos_perdidos'] - empleado['penalizacion_falla_pasado'] + empleado['puntos_ganados'])
            
            # Agregar nivel de riesgo a todos los empleados
            for empleado in empleados_dict.values():
                empleado['nivel_riesgo'] = ResultadoEventoController._determinarNivelRiesgo(empleado['puntos_restantes'])
            
            # Agrupar por área
            areas_dict = {}
            for empleado in empleados_dict.values():
                area_id = empleado['idArea']
                if area_id not in areas_dict:
                    areas_dict[area_id] = {
                        'idArea': empleado['idArea'],
                        'nombreArea': empleado['nombreArea'],
                        'empleados': [],
                        'promedio_puntos': 0,
                        'total_fallas': 0,
                        'total_reportados': 0,
                        'total_eventos': 0,
                        'empleados_con_fallas': 0,
                        'suma_puntos': 0,
                        'total_empleados': 0
                    }
                
                areas_dict[area_id]['empleados'].append(empleado)
                areas_dict[area_id]['suma_puntos'] += empleado['puntos_restantes']
                areas_dict[area_id]['total_empleados'] += 1
                areas_dict[area_id]['total_fallas'] += empleado['total_fallas']
                areas_dict[area_id]['total_reportados'] += empleado['total_reportados']
                areas_dict[area_id]['total_eventos'] += empleado['total_eventos']
                if empleado['total_fallas'] > 0:
                    areas_dict[area_id]['empleados_con_fallas'] += 1
            
            # Calcular promedio de puntos por área y ordenar empleados
            for area in areas_dict.values():
                if area['total_empleados'] > 0:
                    area['promedio_puntos'] = round(area['suma_puntos'] / area['total_empleados'], 2)
                # Ordenar empleados por puntos restantes (descendente - más puntos = mejor)
                area['empleados'].sort(key=lambda x: x['puntos_restantes'], reverse=True)
            
            return jsonify({"areas": list(areas_dict.values())}), 200
            
        except Exception as e:
            log.error(f"Error obteniendo fallas por empleado con scoring: {str(e)}")
            return responseError("ERROR", f"No se pudo obtener el reporte de fallas por empleado: {str(e)}", 500)
        finally:
            session.close()

    @staticmethod
    def _determinarNivelRiesgo(puntos):
        """
        Determina el nivel de riesgo basado en los puntos restantes (100 - puntos_perdidos).
        Sistema invertido: más puntos = menos riesgo
        """
        if puntos >= 100:
            return "Sin riesgo"
        elif puntos >= 90:
            return "Riesgo bajo"
        elif puntos >= 70:
            return "Riesgo medio"
        elif puntos >= 50:
            return "Riesgo alto"
        else:
            return "Riesgo máximo"

    @staticmethod
    def procesarIntentoReporte(idUsuario, tipoEvento, fechaInicio, fechaFin):
        """
        Procesa un intento de reporte de phishing por parte de un empleado.
        Verifica si existe un evento asignado al usuario en el rango de fechas especificado.
        """
        # Resto 3 horas por inconsistencias
        fechaInicio = fechaInicio - timedelta(hours=3)
        fechaFin = fechaFin - timedelta(hours=3)

        session = SessionLocal()
        log.info(f"Se recibio una solicitud para reportar un evento (user: {idUsuario} - tipoEvento: {tipoEvento} - fechaInicio: {fechaInicio} - fechaFin: {fechaFin})")
        try:
            # Crear el intento de reporte (aún sin asociar a un evento específico)
            intento = IntentoReporte(
                idUsuario=idUsuario,
                tipoEvento=tipoEvento,
                fechaInicio=fechaInicio,
                fechaFin=fechaFin,
                fechaIntento=datetime.now()
            )
            log.info("Se crea un intento de reporte")

            # Buscar todos los eventos asignados al usuario en el rango de fechas
            eventos_candidatos = session.query(Evento).join(UsuarioxEvento).filter(
                UsuarioxEvento.idUsuario == idUsuario,
                Evento.tipoEvento == tipoEvento,
                Evento.fechaEvento >= fechaInicio,
                Evento.fechaEvento <= fechaFin
            ).order_by(Evento.fechaEvento.asc()).all()

            evento_encontrado = None

            # Seleccionar el primer evento que NO haya sido ya verificado/reportado previamente por el usuario
            for evento in eventos_candidatos:
                intento_previo = session.query(IntentoReporte).filter_by(
                    idUsuario=idUsuario,
                    idEventoVerificado=evento.idEvento,
                    verificado=True
                ).first()

                if not intento_previo:
                    evento_encontrado = evento
                    break

            if evento_encontrado:
                # Evento nuevo encontrado - marcar como verificado
                log.info("Se encontro un evento elegible para verificar el reporte")
                intento.verificado = True
                intento.idEventoVerificado = evento_encontrado.idEvento
                intento.resultadoVerificacion = f"Evento verificado correctamente. ID: {evento_encontrado.idEvento}"

                # Actualizar el estado del usuarioxevento a REPORTADO
                usuario_evento = session.query(UsuarioxEvento).filter_by(
                    idUsuario=idUsuario,
                    idEvento=evento_encontrado.idEvento
                ).first()

                if usuario_evento:
                    usuario_evento.resultado = ResultadoEvento.REPORTADO
                    usuario_evento.fechaReporte = datetime.now()

                mensaje = "¡Gracias por reportar! El evento ha sido verificado correctamente."
            else:
                if eventos_candidatos:
                    # Había eventos en el rango, pero todos ya habían sido reportados antes
                    log.info("Todos los eventos que coinciden con el rango ya fueron reportados anteriormente por el usuario")
                    intento.verificado = False
                    intento.resultadoVerificacion = "Ya reportaste previamente los eventos que coinciden con el rango indicado. No se encontró un nuevo evento para asociar a este reporte. El evento quedará pendiente para revisión por los administradores"
                    mensaje = "¡Gracias por reportar! Ya habías reportado previamente los eventos de este período, tu nuevo intento quedará pendiente."
                else:
                    # No se encontró ningún evento asignado en ese rango
                    log.info("No se encontro el evento que el usuario indico")
                    intento.verificado = False
                    intento.resultadoVerificacion = "No se encontró un evento asignado en el rango de fechas especificado"
                    mensaje = "¡Gracias por reportar! No se encontró un evento simulado asignado en el rango de fechas especificado. El evento quedará pendiente para revisión por los administradores"
            
            session.add(intento)
            session.commit()
            log.info("Se actualizan las novedades en la BDD")
            
            return jsonify({
                "mensaje": mensaje,
                "verificado": intento.verificado,
                "idIntentoReporte": intento.idIntentoReporte,
                "resultadoVerificacion": intento.resultadoVerificacion
            }), 200
            
        except Exception as e:
            session.rollback()
            log.error(f"Error procesando intento de reporte: {str(e)}")
            return responseError("ERROR", f"Error procesando el reporte: {str(e)}", 500)
        finally:
            session.close()

    @staticmethod
    def obtenerIntentosReportePorUsuario(idUsuario):
        """
        Obtiene todos los intentos de reporte realizados por un usuario específico.
        """
        session = SessionLocal()
        try:
            intentos = session.query(IntentoReporte).filter_by(idUsuario=idUsuario).order_by(
                IntentoReporte.fechaIntento.desc()
            ).all()
            
            return jsonify({
                "intentos": [intento.get() for intento in intentos],
                "total": len(intentos)
            }), 200
            
        except Exception as e:
            log.error(f"Error obteniendo intentos de reporte: {str(e)}")
            return responseError("ERROR", f"Error obteniendo reportes: {str(e)}", 500)
        finally:
            session.close()
