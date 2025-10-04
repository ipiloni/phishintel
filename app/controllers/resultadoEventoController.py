from flask import jsonify
from datetime import datetime
from app.backend.models.error import responseError
from app.backend.models.resultadoEvento import ResultadoEvento
from app.backend.models.usuarioxevento import UsuarioxEvento
from app.backend.models.tipoEvento import TipoEvento
from app.config.db_config import SessionLocal
from app.utils.logger import log

# Variable global para contar fallas
conteo_fallas = {"total": 0}

# Puntos de falla por tipo de evento (se RESTAN del puntaje inicial de 100)
PUNTOS_FALLA = {
    TipoEvento.CORREO: 10,
    TipoEvento.MENSAJE: 15,
    TipoEvento.LLAMADA: 20,
    TipoEvento.VIDEOLLAMADA: 20
}

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

            # Calcular puntos perdidos
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

            # Calcular puntos restantes (100 - puntos_perdidos)
            puntos_restantes = max(0, PUNTAJE_INICIAL - puntos_perdidos)

            # Determinar nivel de riesgo basado en puntos restantes
            nivel_riesgo = ResultadoEventoController._determinarNivelRiesgo(puntos_restantes)

            return jsonify({
                "idUsuario": empleado.idUsuario,
                "nombre": empleado.nombre,
                "apellido": empleado.apellido,
                "puntos_restantes": puntos_restantes,
                "puntos_perdidos": puntos_perdidos,
                "puntaje_inicial": PUNTAJE_INICIAL,
                "total_fallas": total_fallas,
                "nivel_riesgo": nivel_riesgo,
                "desglose_por_tipo": desglose_por_tipo
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
                    'total_fallas': 0,
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
                # Calcular puntos restantes: 100 - puntos perdidos
                empleado['puntos_restantes'] = max(0, PUNTAJE_INICIAL - empleado['puntos_perdidos'])
            
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
                        'total_eventos': 0,
                        'empleados_con_fallas': 0,
                        'suma_puntos': 0,
                        'total_empleados': 0
                    }
                
                areas_dict[area_id]['empleados'].append(empleado)
                areas_dict[area_id]['suma_puntos'] += empleado['puntos_restantes']
                areas_dict[area_id]['total_empleados'] += 1
                areas_dict[area_id]['total_fallas'] += empleado['total_fallas']
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
        if puntos == 100:
            return "Sin riesgo"
        elif puntos >= 90:
            return "Riesgo bajo"
        elif puntos >= 75:
            return "Riesgo medio"
        elif puntos >= 50:
            return "Riesgo alto"
        else:
            return "Riesgo máximo"
