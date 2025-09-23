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
        """
        Determina la clasificación del tiempo de respuesta basada en los objetivos establecidos.
        
        Objetivo ideal (org madura): mediana ≤ 1 hora; P90 ≤ 24 horas.
        Objetivo práctico (estándar): mediana ≤ 4 horas; P90 ≤ 48 horas.
        Línea base (organizaciones en adopción): mediana ≤ 24 horas; P90 ≤ 72 horas.
        """
        
        # Vigilantes del Ciberespacio (Nivel 5) - Objetivo ideal
        if mediana <= 1 and p90 <= 24:
            return "Vigilantes del Ciberespacio", 5, "Responden rápido, con coordinación y apoyo tecnológico avanzado. Mediana ≤ 1h, P90 ≤ 24h"
        
        # Guardianes Anti-Phishing (Nivel 4) - Objetivo ideal con pequeñas desviaciones
        elif mediana <= 2 and p90 <= 36:
            return "Guardianes Anti-Phishing", 4, "Responden rápido, con coordinación y apoyo tecnológico avanzado. Mediana ≤ 2h, P90 ≤ 36h"
        
        # Escudos digitales (Nivel 3) - Objetivo práctico
        elif mediana <= 4 and p90 <= 48:
            return "Escudos digitales", 3, "Respuesta estándar con procesos establecidos. Mediana ≤ 4h, P90 ≤ 48h"
        
        # Aprendices de Seguridad (Nivel 2) - Objetivo práctico con desviaciones
        elif mediana <= 12 and p90 <= 60:
            return "Aprendices de Seguridad", 2, "En proceso de mejora, implementando mejores prácticas. Mediana ≤ 12h, P90 ≤ 60h"
        
        # Presas del Phishing (Nivel 1) - Línea base o peor
        else:
            return "Presas del Phishing", 1, "Necesitan mejorar significativamente sus tiempos de respuesta. Mediana > 12h o P90 > 60h"
