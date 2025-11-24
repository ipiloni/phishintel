from flask import jsonify
from datetime import datetime, timedelta
from app.backend.models.error import responseError
from app.backend.models.area import Area
from app.backend.models.usuario import Usuario
from app.backend.models.evento import Evento
from app.backend.models.registroEvento import RegistroEvento
from app.backend.models.usuarioxevento import UsuarioxEvento
from app.backend.models.intentoReporte import IntentoReporte
from app.backend.models.resultadoEvento import ResultadoEvento
from app.backend.models.tipoEvento import TipoEvento
from app.backend.models.estadoReporte import EstadoReporte
from app.config.db_config import SessionLocal
from app.utils.logger import log
import random
from app.utils.hash import hash_password

class DemoController:
    
    @staticmethod
    def crearUsuariosYAreas(data):
        """
        Crear áreas y usuarios en batch para demo
        """
        session = SessionLocal()
        
        try:
            areas_data = data.get("areas", [])
            usuarios_data = data.get("usuarios", [])
            
            if not areas_data or not usuarios_data:
                return responseError("CAMPOS_OBLIGATORIOS", "Se requieren 'areas' y 'usuarios'", 400)
            
            # Crear áreas
            areas_creadas = []
            for area_data in areas_data:
                area = Area(
                    nombreArea=area_data["nombreArea"]
                )
                session.add(area)
                session.flush()
                areas_creadas.append({
                    "idArea": area.idArea,
                    "nombreArea": area.nombreArea
                })
            
            log.info(f"Se crearon {len(areas_creadas)} áreas")
            
            # Crear usuarios
            usuarios_creados = []
            for usuario_data in usuarios_data:
                hashed = hash_password(usuario_data["password"])  # bcrypt
                usuario = Usuario(
                    nombreUsuario=usuario_data["nombreUsuario"],
                    password=hashed,
                    nombre=usuario_data["nombre"],
                    apellido=usuario_data["apellido"],
                    correo=usuario_data["email"],
                    telefono=usuario_data.get("telefono"),
                    idVoz=usuario_data.get("idVoz"),
                    idArea=usuario_data.get("idArea"),  # Opcional - admin no tiene área
                    esAdministrador=usuario_data.get("esAdministrador", False)
                )
                session.add(usuario)
                session.flush()
                usuarios_creados.append({
                    "idUsuario": usuario.idUsuario,
                    "nombreUsuario": usuario.nombreUsuario,
                    "nombre": usuario.nombre,
                    "apellido": usuario.apellido,
                    "correo": usuario.correo,
                    "telefono": usuario.telefono,
                    "idVoz": usuario.idVoz,
                    "idArea": usuario.idArea,
                    "esAdministrador": usuario.esAdministrador
                })
            
            log.info(f"Se crearon {len(usuarios_creados)} usuarios")
            
            session.commit()
            
            return jsonify({
                "mensaje": "Áreas y usuarios creados exitosamente",
                "areas": areas_creadas,
                "usuarios": usuarios_creados
            }), 201
            
        except Exception as e:
            session.rollback()
            log.error(f"Error creando áreas y usuarios: {str(e)}")
            return responseError("ERROR", f"Error creando áreas y usuarios: {str(e)}", 500)
        finally:
            session.close()
    
    @staticmethod
    def crearEventosEIntentosReporte(data):
        """
        Crear eventos, resultados e intentos de reporte para demo
        Área 3 (Compras) tendrá buen comportamiento con muchos reportes
        Área 2 (RRHH) tendrá mal comportamiento
        Área 1 (Ventas) estará vacía para pruebas
        """
        session = SessionLocal()
        
        try:
            eventos_data = data.get("eventos", [])
            
            if not eventos_data:
                return responseError("CAMPOS_OBLIGATORIOS", "Se requiere al menos un evento", 400)
            
            eventos_creados = []
            resultados_creados = []
            intentos_creados = []
            
            for evento_data in eventos_data:
                if not evento_data.get("tipoEvento") or not evento_data.get("asunto"):
                    continue
                
                tipo_evento = TipoEvento(evento_data["tipoEvento"])
                fecha_evento = datetime.fromisoformat(evento_data["fechaEvento"])
                
                # Asignar dificultad
                dificultad = None
                if tipo_evento in [TipoEvento.MENSAJE, TipoEvento.CORREO]:
                    dificultad = evento_data.get("dificultad", random.choice(["Fácil", "Medio", "Difícil"]))
                
                # Asignar medio para mensajes
                medio = None
                if tipo_evento == TipoEvento.MENSAJE:
                    medio = evento_data.get("medio", random.choice(["whatsapp", "telegram", "sms"]))
                
                # Crear evento
                evento = Evento(
                    tipoEvento=tipo_evento,
                    fechaEvento=fecha_evento,
                    dificultad=dificultad,
                    medio=medio
                )
                session.add(evento)
                session.flush()
                
                # Crear registro del evento
                remitente = evento_data.get("remitente")
                # Para llamadas, si no se especifica remitente, usamos uno aleatorio
                if tipo_evento == TipoEvento.LLAMADA and not remitente:
                    posibles_remitentes = [
                        "Soporte IT",
                        "Mesa de Ayuda",
                        "Recursos Humanos",
                        "Seguridad Informática",
                        "Administración",
                        "Proveedor Externo",
                        "Banco Central",
                        "AFIP",
                        "Gerencia General"
                    ]
                    remitente = random.choice(posibles_remitentes)
                
                registro = RegistroEvento(
                    idEvento=evento.idEvento,
                    asunto=evento_data["asunto"],
                    cuerpo=evento_data.get("cuerpo"),
                    mensaje=evento_data.get("mensaje"),
                    remitente=remitente
                )
                session.add(registro)
                
                # Obtener usuarios para este evento
                usuarios_evento = evento_data.get("usuarios", [])
                
                # Crear resultados e intentos de reporte
                for idUsuario in usuarios_evento:
                    # Obtener área del usuario
                    usuario = session.query(Usuario).filter_by(idUsuario=idUsuario).first()
                    if not usuario:
                        continue
                    
                    idArea = usuario.idArea
                    
                    # Lógica según área
                    # Área 3 (Compras): Buen comportamiento - Alta tasa de reporte
                    # Área 2: Mal comportamiento - Alta tasa de falla
                    # Área 1: Vacía para pruebas
                    
                    rand = random.random()
                    esFallaGrave = False
                    fechaFalla = None
                    fechaReporte = None
                    haFalladoEnElPasado = False
                    resultado = None
                    
                    if idArea == 3:  # Área de Compras - Buen comportamiento
                        if rand < 0.7:  # 70% reporta correctamente
                            resultado = ResultadoEvento.REPORTADO
                            fechaReporte = fecha_evento + timedelta(minutes=random.randint(10, 120))
                            
                            # Crear intento de reporte que llevó a este resultado
                            # El intento debe ser antes de la fecha de reporte
                            fecha_intento = fechaReporte - timedelta(minutes=random.randint(1, 5))
                            
                            intento = IntentoReporte(
                                idUsuario=idUsuario,
                                tipoEvento=tipo_evento.value,
                                fechaInicio=fecha_evento - timedelta(hours=1),
                                fechaFin=fecha_evento + timedelta(hours=1),
                                fechaIntento=fecha_intento,
                                verificado=True,
                                estado=EstadoReporte.VERIFICADO,
                                resultadoVerificacion=f"Evento verificado correctamente. ID: {evento.idEvento}",
                                idEventoVerificado=evento.idEvento,
                                observaciones="Reporte generado automáticamente en demo - Buen comportamiento"
                            )
                            session.add(intento)
                            intentos_creados.append({
                                "idUsuario": idUsuario,
                                "tipoEvento": tipo_evento.value,
                                "verificado": True
                            })
                            
                        elif rand < 0.85:  # 15% reporta con falla previa
                            resultado = ResultadoEvento.REPORTADO
                            fechaFalla = fecha_evento + timedelta(minutes=random.randint(5, 30))
                            fechaReporte = fechaFalla + timedelta(minutes=random.randint(10, 60))
                            haFalladoEnElPasado = True
                            esFallaGrave = False
                            
                            # Crear intento de reporte
                            fecha_intento = fechaReporte - timedelta(minutes=random.randint(1, 5))
                            
                            intento = IntentoReporte(
                                idUsuario=idUsuario,
                                tipoEvento=tipo_evento.value,
                                fechaInicio=fecha_evento - timedelta(hours=1),
                                fechaFin=fecha_evento + timedelta(hours=1),
                                fechaIntento=fecha_intento,
                                verificado=True,
                                estado=EstadoReporte.VERIFICADO,
                                resultadoVerificacion=f"Evento verificado correctamente. ID: {evento.idEvento}",
                                idEventoVerificado=evento.idEvento,
                                observaciones="Reporte tras falla - Usuario aprendió del error"
                            )
                            session.add(intento)
                            intentos_creados.append({
                                "idUsuario": idUsuario,
                                "tipoEvento": tipo_evento.value,
                                "verificado": True
                            })
                            
                        else:  # 15% pendiente
                            resultado = ResultadoEvento.PENDIENTE
                    
                    elif idArea == 2:  # Mal comportamiento
                        if rand < 0.6:  # 60% falla
                            resultado = ResultadoEvento.FALLA
                            fechaFalla = fecha_evento + timedelta(minutes=random.randint(5, 60))
                            haFalladoEnElPasado = True
                            esFallaGrave = random.random() < 0.5  # 50% de fallas son graves (un poco más para que se vean)
                        elif rand < 0.75:  # 15% reporta
                            resultado = ResultadoEvento.REPORTADO
                            fechaReporte = fecha_evento + timedelta(minutes=random.randint(30, 240))
                            
                            # Crear intento de reporte
                            fecha_intento = fechaReporte - timedelta(minutes=random.randint(1, 5))
                            
                            intento = IntentoReporte(
                                idUsuario=idUsuario,
                                tipoEvento=tipo_evento.value,
                                fechaInicio=fecha_evento - timedelta(hours=1),
                                fechaFin=fecha_evento + timedelta(hours=1),
                                fechaIntento=fecha_intento,
                                verificado=True,
                                estado=EstadoReporte.VERIFICADO,
                                resultadoVerificacion=f"Evento verificado correctamente. ID: {evento.idEvento}",
                                idEventoVerificado=evento.idEvento,
                                observaciones="Reporte tardío - Área con bajo rendimiento"
                            )
                            session.add(intento)
                            intentos_creados.append({
                                "idUsuario": idUsuario,
                                "tipoEvento": tipo_evento.value,
                                "verificado": True
                            })
                        else:  # 25% pendiente
                            resultado = ResultadoEvento.PENDIENTE
                    
                    else:  # Área 1 u otras - Vacías para pruebas
                        resultado = ResultadoEvento.PENDIENTE
                    
                    # Crear UsuarioxEvento
                    usuario_evento = UsuarioxEvento(
                        idUsuario=idUsuario,
                        idEvento=evento.idEvento,
                        resultado=resultado,
                        fechaFalla=fechaFalla,
                        fechaReporte=fechaReporte,
                        esFallaGrave=esFallaGrave,
                        haFalladoEnElPasado=haFalladoEnElPasado
                    )
                    session.add(usuario_evento)
                    resultados_creados.append({
                        "idUsuario": idUsuario,
                        "idEvento": evento.idEvento,
                        "resultado": resultado.value
                    })
                
                eventos_creados.append({
                    "idEvento": evento.idEvento,
                    "tipoEvento": tipo_evento.value,
                    "fechaEvento": fecha_evento.isoformat()
                })
            
            session.commit()
            log.info(f"Demo creada: {len(eventos_creados)} eventos, {len(resultados_creados)} resultados, {len(intentos_creados)} intentos de reporte")
            
            return jsonify({
                "mensaje": "Demo creada exitosamente",
                "eventos": len(eventos_creados),
                "resultados": len(resultados_creados),
                "intentos_reporte": len(intentos_creados),
                "detalle": {
                    "eventos_creados": eventos_creados[:5],  # Mostrar solo los primeros 5
                    "total_eventos": len(eventos_creados)
                }
            }), 201
            
        except Exception as e:
            session.rollback()
            log.error(f"Error creando demo: {str(e)}")
            return responseError("ERROR", f"Error creando demo: {str(e)}", 500)
        finally:
            session.close()
