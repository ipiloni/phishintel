import datetime
import requests

from flask import jsonify

from app.backend.models.error import responseError
from app.backend.models import RegistroEvento, Usuario
from app.backend.models.evento import Evento
from app.backend.models.resultadoEvento import ResultadoEvento
from app.backend.models.tipoEvento import TipoEvento
from app.backend.models.usuarioxevento import UsuarioxEvento
from app.config.db_config import SessionLocal
from app.utils.config import get
from app.utils.logger import log
from app.utils.url_encoder import build_phishing_url

# Importar los nuevos controladores
from app.controllers.mensajes.whatsapp import WhatsAppController
from app.controllers.mensajes.telegram import TelegramController, telegram_bot
from app.controllers.mensajes.sms import SMSController


class MsjController:

    @staticmethod
    def enviarMensajePorID(data):
        """
        Envía un mensaje de phishing a un usuario específico por ID.
        Crea un evento de tipo MENSAJE y genera un enlace para reportar falla.
        
        Args:
            data (dict): Diccionario con los siguientes campos:
                - medio (str): Medio de comunicación ('whatsapp', 'telegram', 'sms')
                - idUsuario (int): ID del usuario al que enviar el mensaje
                - mensaje (str): Contenido del mensaje
                - dificultad (str): Nivel de dificultad ('Fácil', 'Medio', 'Difícil')
                - proveedor (str, opcional): Proveedor específico dentro del medio (hardcodeado según medio)
                    - Para whatsapp: 'whapi-link-preview'
                    - Para telegram: 'telethon'
                    - Para sms: 'textBee'
        """
        if not data or "medio" not in data or "idUsuario" not in data or "mensaje" not in data:
            return responseError("CAMPOS_OBLIGATORIOS",
                                 "Faltan campos obligatorios como 'medio', 'idUsuario' o 'mensaje'", 400)

        medio = data["medio"]
        id_usuario = data["idUsuario"]
        mensaje = data["mensaje"]
        dificultad = data.get("dificultad", "Fácil")

        log.info(f"Enviando mensaje por ID - Medio: {medio}, ID Usuario: {id_usuario}, Dificultad: {dificultad}")

        session = SessionLocal()
        try:
            # Buscar el usuario en la BD
            usuario = session.query(Usuario).filter_by(idUsuario=id_usuario).first()
            if not usuario:
                session.close()
                log.error(f"Usuario no encontrado con ID: {id_usuario}")
                return responseError("USUARIO_NO_ENCONTRADO",
                                     f"No se encontró el usuario con ID {id_usuario}", 404)

            # Crear el evento y registro
            registroEvento = RegistroEvento(asunto="Mensaje de Phishing", cuerpo=mensaje)
            evento = Evento(
                tipoEvento=TipoEvento.MENSAJE,
                fechaEvento=datetime.datetime.now(),
                registroEvento=registroEvento
            )
            session.add(evento)
            session.commit()  # Para obtener idEvento

            # Vincular el evento con el usuario
            usuario_evento = UsuarioxEvento(
                idUsuario=id_usuario,
                idEvento=evento.idEvento,
                resultado=ResultadoEvento.PENDIENTE
            )
            session.add(usuario_evento)
            session.commit()

            # Obtener URL_APP del properties.env
            url_app = get("URL_APP")
            if not url_app:
                url_app = "http://localhost:8080"  # Fallback si no está configurado
                log.warn("URL_APP no configurada, usando fallback: http://localhost:8080")

            # Determinar ruta según dificultad
            if dificultad.lower() in ["medio", "media"]:
                # Dificultad Media: Usar caisteLogin para mayor realismo
                ruta_interna = "caisteLogin"
            elif dificultad.lower() in ["difícil", "dificil"]:
                # Dificultad Difícil: Usar caisteDatos para solicitar datos sensibles
                ruta_interna = "caisteDatos"
            else:
                # Dificultad Fácil: Usar caiste directamente
                ruta_interna = "caiste"

            # Construir URL codificada para phishing (encubierta)
            link_caiste = build_phishing_url(url_app, ruta_interna, id_usuario, evento.idEvento)

            mensaje_con_enlace = f"{mensaje}\n\n🔗 Enlace: {link_caiste}"
            mensaje_html = f"{mensaje}\n\n🔗 <a href=\"{link_caiste}\">Click Aqui</a>"

            # Enviar mensaje según el medio (con proveedor hardcodeado)
            if medio == "whatsapp":
                # Hardcodear proveedor para WhatsApp
                proveedor = "whapi-link-preview"
                
                if not usuario.telefono:
                    session.rollback()
                    return responseError("TELEFONO_NO_REGISTRADO", "El usuario no tiene teléfono registrado", 404)
                
                # Usar WhatsApp whapi con link preview
                # El mensaje debe contener un enlace placeholder que será reemplazado por el enlace real usando URL_APP
                mensaje_con_enlace_placeholder = f"{mensaje}\n\n🔗 Enlace: http://placeholder.com"
                result = WhatsAppController.enviarMensajeWhapiLinkPreview({
                    "mensaje": mensaje_con_enlace_placeholder,
                    "destinatario": usuario.telefono,
                    "titulo": "Enlace",
                    "idUsuario": id_usuario,
                    "idEvento": evento.idEvento,
                    "rutaEnlace": ruta_interna
                })

            elif medio == "telegram":
                # Hardcodear proveedor para Telegram
                proveedor = "telethon"
                
                log.info(f"Enviando mensaje Telegram con Telethon para usuario {usuario.nombre} {usuario.apellido}")
                
                if not usuario.telefono:
                    session.rollback()
                    log.error(f"Usuario {id_usuario} ({usuario.nombre} {usuario.apellido}) no tiene teléfono registrado")
                    return responseError("TELEFONO_NO_REGISTRADO", f"El usuario {usuario.nombre} {usuario.apellido} no tiene teléfono registrado", 404)
                
                # Usar Telegram Telethon (cuenta propia)
                result = TelegramController.enviarMensajeTelethon({
                    "mensaje": mensaje_html,
                    "destinatario": usuario.telefono
                })

            elif medio == "sms":
                # Hardcodear proveedor para SMS
                proveedor = "textBee"
                
                if not usuario.telefono:
                    session.rollback()
                    return responseError("TELEFONO_NO_REGISTRADO", "El usuario no tiene teléfono registrado", 404)
                
                # Usar SMS TextBee
                result = SMSController.enviarMensajeTextBee({
                    "mensaje": mensaje_con_enlace,
                    "destinatario": usuario.telefono
                })

            else:
                session.rollback()
                return responseError("MEDIO_INVALIDO", "Medio no reconocido. Use 'whatsapp', 'telegram' o 'sms'", 400)

            # Verificar si el envío fue exitoso
            if isinstance(result, tuple) and len(result) == 2:
                response, status_code = result
                if status_code >= 400:
                    session.rollback()
                    return result

            idnuevo = evento.idEvento
            session.close()
            return jsonify({"mensaje": "Mensaje enviado correctamente", "idEvento": idnuevo}), 201

        except Exception as e:
            log.error(f"Error en enviarMensajePorID: {str(e)}")
            session.rollback()
            session.close()
            return responseError("ERROR", f"Hubo un error al enviar mensaje: {str(e)}", 500)
