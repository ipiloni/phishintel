from flask import jsonify
from sqlalchemy import func, and_
from sqlalchemy.orm import joinedload
from app.backend.models import Usuario
from app.backend.models.usuarioxevento import UsuarioxEvento
from app.backend.models.resultadoEvento import ResultadoEvento
from app.backend.models.evento import Evento
from app.backend.models.error import responseError
from app.config.db_config import SessionLocal

class ControllerKpis:

    @staticmethod
    def obtenerTiempoRespuestaPromedio():
        """
        Calcula el tiempo de respuesta promedio para eventos reportados por usuarios.
        La diferencia en horas entre fecha_reporte (usuarioxevento) y fechaEvento (evento).
        """
        session = SessionLocal()
        try:
            # Usar la misma estructura que el endpoint de eventos
            eventos = session.query(Evento).options(
                joinedload(Evento.usuariosAsociados)
            ).all()
            
            diferencias_horas = []
            
            for evento in eventos:
                for ux in evento.usuariosAsociados:
                    # Verificar si es REPORTADO y tiene fechaReporte
                    if ux.resultado.value == "REPORTADO" and ux.fechaReporte is not None:
                        try:
                            # Calcular diferencia en horas
                            diff_seconds = (ux.fechaReporte - evento.fechaEvento).total_seconds()
                            horas = diff_seconds / 3600
                            
                            if horas >= 0:  # Solo diferencias positivas
                                diferencias_horas.append(horas)
                        except Exception as e:
                            print(f"Error calculando diferencia: {e}")
                            continue
            
            if not diferencias_horas:
                return jsonify({
                    "tiempoRespuestaPromedio": 0,
                    "tiempoRespuestaMediana": 0,
                    "tiempoRespuestaP90": 0,
                    "totalEventosReportados": 0,
                    "clasificacion": "Sin datos",
                    "nivel": 0,
                    "descripcion": "No hay eventos reportados válidos para calcular el tiempo de respuesta"
                }), 200
            
            # Calcular estadísticas
            total_eventos = len(diferencias_horas)
            tiempo_promedio = sum(diferencias_horas) / total_eventos
            
            # Calcular mediana
            diferencias_ordenadas = sorted(diferencias_horas)
            n = len(diferencias_ordenadas)
            if n % 2 == 0:
                mediana = (diferencias_ordenadas[n//2 - 1] + diferencias_ordenadas[n//2]) / 2
            else:
                mediana = diferencias_ordenadas[n//2]
            
            # Calcular P90 (percentil 90)
            indice_p90 = int(0.9 * n)
            if indice_p90 >= n:
                indice_p90 = n - 1
            p90 = diferencias_ordenadas[indice_p90]
            
            # Determinar clasificación basada en los objetivos
            clasificacion, nivel, descripcion = ControllerKpis._determinarClasificacionTiempoRespuesta(mediana, p90)
            
            return jsonify({
                "tiempoRespuestaPromedio": round(tiempo_promedio, 2),
                "tiempoRespuestaMediana": round(mediana, 2),
                "tiempoRespuestaP90": round(p90, 2),
                "totalEventosReportados": total_eventos,
                "clasificacion": clasificacion,
                "nivel": nivel,
                "descripcion": descripcion
            }), 200
            
        except Exception as e:
            session.rollback()
            return responseError("ERROR", f"No se pudo calcular el tiempo de respuesta promedio: {str(e)}", 500)
        finally:
            session.close()

    @staticmethod
    def _determinarClasificacionTiempoRespuesta(mediana, p90):
        
        # Vigilantes del Ciberespacio (Nivel 5) - Objetivo ideal
        if mediana <= 1 and p90 <= 24:
            return "Vigilantes del Ciberespacio", 5, "Excelencia en ciberseguridad con respuesta ultrarrápida y tecnología de vanguardia. Mediana ≤ 1h, P90 ≤ 24h"
        
        # Guardianes Anti-Phishing (Nivel 4) - Objetivo ideal con pequeñas desviaciones
        elif mediana <= 2 and p90 <= 36:
            return "Guardianes Anti-Phishing", 4, "Responden rápido, con coordinación y apoyo tecnológico avanzado. Mediana ≤ 2h, P90 ≤ 36h"
        
        # Defensores Digitales (Nivel 3) - Objetivo práctico
        elif mediana <= 4 and p90 <= 48:
            return "Defensores Digitales", 3, "Respuesta estándar con procesos establecidos. Mediana ≤ 4h, P90 ≤ 48h"
        
        # Aprendices de Seguridad (Nivel 2) - Objetivo práctico con desviaciones
        elif mediana <= 12 and p90 <= 60:
            return "Aprendices de Seguridad", 2, "En proceso de mejora, implementando mejores prácticas. Mediana ≤ 12h, P90 ≤ 60h"
        
        # Presas del Phishing (Nivel 1) - Línea base o peor
        else:
            return "Presas del Phishing", 1, "Necesitan mejorar significativamente sus tiempos de respuesta. Mediana > 12h o P90 > 60h"

    @staticmethod
    def obtenerTasaFallas():
        """
        Calcula la tasa de fallas basada en los intentos de phishing (usuarios asignados a eventos).
        Cada usuario asignado a un evento representa un intento de phishing individual.
        Calcula el porcentaje de intentos que resultaron en FALLA.
        """
        session = SessionLocal()
        try:
            # Obtener todas las relaciones usuarioxevento (intentos de phishing)
            intentos_phishing = session.query(UsuarioxEvento).all()
            
            total_intentos = len(intentos_phishing)
            intentos_con_falla = 0
            
            for intento in intentos_phishing:
                # Verificar si el resultado del intento es FALLA
                if intento.resultado.value == "FALLA":
                    intentos_con_falla += 1
            
            # Validar si hay suficientes intentos de phishing para mostrar el KPI
            if total_intentos < 5:
                return jsonify({
                    "tasaFallas": 0,
                    "totalIntentos": total_intentos,
                    "intentosConFalla": intentos_con_falla,
                    "intentosSinFalla": total_intentos - intentos_con_falla,
                    "clasificacion": "Datos Insuficientes",
                    "nivel": 0,
                    "descripcion": f"Acumule más intentos de phishing para ver el KPI. Actualmente tiene {total_intentos} intentos, se requieren al menos 5.",
                    "insuficienteDatos": True
                }), 200
            
            # Calcular tasa de fallas
            tasa_fallas = (intentos_con_falla / total_intentos) * 100
            
            # Determinar clasificación basada en la tasa de fallas
            clasificacion, nivel, descripcion = ControllerKpis._determinarClasificacionTasaFallas(tasa_fallas)
            
            return jsonify({
                "tasaFallas": round(tasa_fallas, 2),
                "totalIntentos": total_intentos,
                "intentosConFalla": intentos_con_falla,
                "intentosSinFalla": total_intentos - intentos_con_falla,
                "clasificacion": clasificacion,
                "nivel": nivel,
                "descripcion": descripcion,
                "insuficienteDatos": False
            }), 200
            
        except Exception as e:
            session.rollback()
            return responseError("ERROR", f"No se pudo calcular la tasa de fallas: {str(e)}", 500)
        finally:
            session.close()

    @staticmethod
    def _determinarClasificacionTasaFallas(tasa_fallas):
        """
        Determina la clasificación basada en la tasa de fallas según los criterios definidos.
        """
        # Vigilantes del Ciberespacio (Nivel 5) – Excelencia en ciberseguridad
        if tasa_fallas <= 2:
            return "Vigilantes del Ciberespacio", 5, "Operación prácticamente sin fallas, con control casi perfecto. Failure Rate ≤ 2%"
        
        # Guardianes Anti-Phishing (Nivel 4) – Alto rendimiento con pequeñas desviaciones
        elif tasa_fallas <= 5:
            return "Guardianes Anti-Phishing", 4, "Fallas puntuales, dentro de lo aceptable en un entorno exigente. Failure Rate > 2% y ≤ 5%"
        
        # Defensores Digitales (Nivel 3) – Objetivo práctico
        elif tasa_fallas <= 10:
            return "Defensores Digitales", 3, "Rendimiento estándar, fallas presentes pero controlables. Failure Rate > 5% y ≤ 10%"
        
        # Aprendices de Seguridad (Nivel 2) – En proceso de mejora
        elif tasa_fallas <= 20:
            return "Aprendices de Seguridad", 2, "Fallas frecuentes, requieren refuerzo de procesos y controles. Failure Rate > 10% y ≤ 20%"
        
        # Presas del Phishing (Nivel 1) – Necesitan mejorar significativamente
        else:
            return "Presas del Phishing", 1, "Nivel crítico de fallas, con alto riesgo operativo y reputacional. Failure Rate > 20%"
