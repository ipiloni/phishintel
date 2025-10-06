from flask import jsonify
from datetime import datetime
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

# Puntos de falla por tipo de evento (se RESTAN del puntaje inicial de 100)
PUNTOS_FALLA = {
    TipoEvento.CORREO: 10,
    TipoEvento.MENSAJE: 15,
    TipoEvento.LLAMADA_SMS: 20,
    TipoEvento.LLAMADA_CORREO: 20,
    TipoEvento.LLAMADA_WPP: 20
}

# Puntos por evento reportado (se SUMAN al puntaje)
PUNTOS_REPORTADO = 5

# Puntaje inicial para todos los empleados
PUNTAJE_INICIAL = 100

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
            # Marcar que ha fallado en el pasado
            usuario_evento.haFalladoEnElPasado = True
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

            # Obtener fallas del empleado
            fallas = (
                session.query(
                    Evento.tipoEvento,
                    func.count(UsuarioxEvento.idEvento).label("cantidad_fallas")
                )
                .join(UsuarioxEvento, UsuarioxEvento.idEvento == Evento.idEvento)
                .filter(UsuarioxEvento.idUsuario == idUsuario)
                .filter(UsuarioxEvento.resultado == ResultadoEvento.FALLA)
                .group_by(Evento.tipoEvento)
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

            # Calcular puntos perdidos por fallas
            puntos_perdidos = 0
            total_fallas = 0
            desglose_por_tipo = {}

            for falla in fallas:
                cantidad = int(falla.cantidad_fallas)
                puntos_tipo = PUNTOS_FALLA.get(falla.tipoEvento, 0)
                puntos_perdidos += cantidad * puntos_tipo
                total_fallas += cantidad
                desglose_por_tipo[falla.tipoEvento.value] = {
                    "cantidad": cantidad,
                    "puntos_perdidos": cantidad * puntos_tipo
                }

            # Calcular puntos ganados por reportes
            puntos_ganados = int(reportados) * PUNTOS_REPORTADO

            # Calcular penalización por fallas en el pasado basada en el tipo de evento
            penalizacion_falla_pasado = 0
            ha_fallado_en_pasado = False
            
            # Obtener fallas del pasado por tipo de evento (incluyendo las que fueron reportadas después)
            fallas_pasado = (
                session.query(
                    Evento.tipoEvento,
                    func.count(UsuarioxEvento.idEvento).label("cantidad_fallas_pasado")
                )
                .join(UsuarioxEvento, UsuarioxEvento.idEvento == Evento.idEvento)
                .filter(UsuarioxEvento.idUsuario == idUsuario)
                .filter(UsuarioxEvento.haFalladoEnElPasado == True)
                .filter(UsuarioxEvento.resultado != ResultadoEvento.FALLA)  # Excluir solo fallas activas
                .group_by(Evento.tipoEvento)
                .all()
            )
            
            # Calcular penalización total por fallas en el pasado
            for falla_pasado in fallas_pasado:
                cantidad = int(falla_pasado.cantidad_fallas_pasado)
                puntos_tipo = PUNTOS_FALLA.get(falla_pasado.tipoEvento, 0)
                penalizacion_falla_pasado += cantidad * puntos_tipo
                ha_fallado_en_pasado = True

            # Calcular puntos restantes (100 - puntos_perdidos - penalizacion_falla_pasado + puntos_ganados)
            puntos_restantes = max(0, PUNTAJE_INICIAL - puntos_perdidos - penalizacion_falla_pasado + puntos_ganados)

            # Determinar nivel de riesgo basado en puntos restantes
            nivel_riesgo = ResultadoEventoController._determinarNivelRiesgo(puntos_restantes)

            # Obtener eventos específicos para el desglose detallado
            from app.backend.models.registroEvento import RegistroEvento
            
            # 1. Fallas activas (sin reportar)
            eventos_activos = (
                session.query(Evento, RegistroEvento)
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
                            "titulo": registro.asunto if registro and registro.asunto else f"Evento {evento.tipoEvento.value}",
                            "tipoEvento": evento.tipoEvento.value,
                            "fechaCreacion": evento.fechaEvento.isoformat() if evento.fechaEvento else None,
                            "puntos": PUNTOS_FALLA.get(evento.tipoEvento, 0),
                            "tipo": "falla_activa"
                        } for evento, registro in eventos_activos
                    ],
                    "reportados": [
                        {
                            "idEvento": evento.idEvento,
                            "titulo": registro.asunto if registro and registro.asunto else f"Evento {evento.tipoEvento.value}",
                            "tipoEvento": evento.tipoEvento.value,
                            "fechaCreacion": evento.fechaEvento.isoformat() if evento.fechaEvento else None,
                            "puntos": PUNTOS_REPORTADO,
                            "haFalladoEnElPasado": usuario_evento.haFalladoEnElPasado,
                            "puntosFallaPasada": PUNTOS_FALLA.get(evento.tipoEvento, 0) if usuario_evento.haFalladoEnElPasado else 0,
                            "tipo": "falla_reportada" if usuario_evento.haFalladoEnElPasado else "reportado"
                        } for evento, registro, usuario_evento in eventos_reportados
                    ],
                    "pendientes": [
                        {
                            "idEvento": evento.idEvento,
                            "titulo": registro.asunto if registro and registro.asunto else f"Evento {evento.tipoEvento.value}",
                            "tipoEvento": evento.tipoEvento.value,
                            "fechaCreacion": evento.fechaEvento.isoformat() if evento.fechaEvento else None,
                            "puntos": 0,
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
            
            # Ahora obtener las fallas de los empleados que las tienen
            query_fallas = (
                session.query(
                    Area.idArea,
                    Area.nombreArea,
                    Usuario.idUsuario,
                    Usuario.nombre,
                    Usuario.apellido,
                    Evento.tipoEvento,
                    func.count(UsuarioxEvento.idEvento).label("cantidad_fallas")
                )
                .join(Usuario, Usuario.idArea == Area.idArea)
                .join(UsuarioxEvento, UsuarioxEvento.idUsuario == Usuario.idUsuario)
                .join(Evento, Evento.idEvento == UsuarioxEvento.idEvento)
                .filter(UsuarioxEvento.resultado == ResultadoEvento.FALLA)
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
            
            resultados_fallas = (
                query_fallas.group_by(
                    Area.idArea,
                    Area.nombreArea,
                    Usuario.idUsuario,
                    Usuario.nombre,
                    Usuario.apellido,
                    Evento.tipoEvento
                )
                .all()
            )
            
            # Procesar las fallas y actualizar el diccionario de empleados
            for r in resultados_fallas:
                empleado_key = f"{r.idArea}_{r.idUsuario}"
                
                if empleado_key in empleados_dict:
                    empleado = empleados_dict[empleado_key]
                    cantidad_fallas = int(r.cantidad_fallas)
                    puntos_tipo = PUNTOS_FALLA.get(r.tipoEvento, 0)
                    puntos_perdidos = cantidad_fallas * puntos_tipo
                    
                    empleado['puntos_perdidos'] += puntos_perdidos
                    empleado['total_fallas'] += cantidad_fallas
                    empleado['fallas_por_tipo'][r.tipoEvento.value] = cantidad_fallas
            
            # Procesar eventos reportados y actualizar el diccionario de empleados
            for r in query_reportados:
                empleado_key = f"{r.idArea}_{r.idUsuario}"
                
                if empleado_key in empleados_dict:
                    empleado = empleados_dict[empleado_key]
                    cantidad_reportados = int(r.cantidad_reportados)
                    puntos_ganados = cantidad_reportados * PUNTOS_REPORTADO
                    
                    empleado['puntos_ganados'] = puntos_ganados
                    empleado['total_reportados'] = cantidad_reportados
            
            # Obtener fallas del pasado por tipo de evento para todos los empleados (incluyendo las que fueron reportadas después)
            query_falla_pasado = (
                session.query(
                    Area.idArea,
                    Usuario.idUsuario,
                    Evento.tipoEvento,
                    func.count(UsuarioxEvento.idEvento).label("cantidad_fallas_pasado")
                )
                .join(Usuario, Usuario.idArea == Area.idArea)
                .join(UsuarioxEvento, UsuarioxEvento.idUsuario == Usuario.idUsuario)
                .join(Evento, Evento.idEvento == UsuarioxEvento.idEvento)
                .filter(UsuarioxEvento.haFalladoEnElPasado == True)
                .filter(UsuarioxEvento.resultado != ResultadoEvento.FALLA)  # Excluir solo fallas activas
                .group_by(Area.idArea, Usuario.idUsuario, Evento.tipoEvento)
                .all()
            )
            
            # Procesar fallas del pasado por tipo de evento
            for r in query_falla_pasado:
                empleado_key = f"{r.idArea}_{r.idUsuario}"
                if empleado_key in empleados_dict:
                    cantidad = int(r.cantidad_fallas_pasado)
                    puntos_tipo = PUNTOS_FALLA.get(r.tipoEvento, 0)
                    penalizacion = cantidad * puntos_tipo
                    
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
        elif puntos >= 75:
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
        session = SessionLocal()
        try:
            # Crear el intento de reporte
            intento = IntentoReporte(
                idUsuario=idUsuario,
                tipoEvento=tipoEvento,
                fechaInicio=fechaInicio,
                fechaFin=fechaFin,
                fechaIntento=datetime.now()
            )
            
            # Buscar si existe un evento asignado al usuario en el rango de fechas
            evento_encontrado = session.query(Evento).join(UsuarioxEvento).filter(
                UsuarioxEvento.idUsuario == idUsuario,
                Evento.tipoEvento == tipoEvento,
                Evento.fechaEvento >= fechaInicio,
                Evento.fechaEvento <= fechaFin
            ).first()
            
            if evento_encontrado:
                # Evento encontrado - marcar como verificado
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
                # No se encontró evento - marcar como no verificado
                intento.verificado = False
                intento.resultadoVerificacion = "No se encontró un evento asignado en el rango de fechas especificado"
                mensaje = "¡Gracias por reportar! Sin embargo, no se encontró un evento asignado en el rango de fechas especificado."
            
            session.add(intento)
            session.commit()
            
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
