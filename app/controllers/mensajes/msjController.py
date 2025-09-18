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
                - proveedor (str, opcional): Proveedor específico dentro del medio
                    - Para whatsapp: 'twilio', 'selenium', 'whapi', 'whapi-link-preview'
                    - Para telegram: 'bot'
                    - Para sms: 'twilio'
        """
        if not data or "medio" not in data or "idUsuario" not in data or "mensaje" not in data:
            return responseError("CAMPOS_OBLIGATORIOS",
                                 "Faltan campos obligatorios como 'medio', 'idUsuario' o 'mensaje'", 400)

        medio = data["medio"]
        proveedor = data.get("proveedor", "")
        id_usuario = data["idUsuario"]
        mensaje = data["mensaje"]

        session = SessionLocal()
        try:
            # Buscar el usuario en la BD
            usuario = session.query(Usuario).filter_by(idUsuario=id_usuario).first()
            if not usuario:
                session.close()
                return responseError("USUARIO_NO_ENCONTRADO",
                                     "No se encontró el usuario", 404)

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

            # Construir link a caiste con parámetros y agregar al mensaje
            link_caiste = f"http://localhost:8080/caiste?idUsuario={id_usuario}&idEvento={evento.idEvento}"
            mensaje_con_enlace = f"{mensaje}\n\n🔗 Enlace: {link_caiste}"


            # Enviar mensaje según el medio
            if medio == "whatsapp":
                if proveedor == "twilio":
                    if not usuario.telefono:
                        session.rollback()
                        return responseError("TELEFONO_NO_REGISTRADO", "El usuario no tiene teléfono registrado", 404)
                    
                    # Usar WhatsApp Twilio
                    result = WhatsAppController.enviarMensajeTwilio({
                        "mensaje": mensaje_con_enlace,
                        "destinatario": usuario.telefono
                    })
                    
                elif proveedor == "selenium":
                    if not usuario.telefono:
                        session.rollback()
                        return responseError("TELEFONO_NO_REGISTRADO", "El usuario no tiene teléfono registrado", 404)
                    
                    # Usar WhatsApp Selenium
                    result = WhatsAppController.enviarMensajeSelenium({
                        "mensaje": mensaje_con_enlace,
                        "destinatario": usuario.telefono
                    })
                    
                elif proveedor == "whapi":
                    usuario.telefono = "+54 9 11 4163-5935"
                    if not usuario.telefono:
                        session.rollback()
                        return responseError("TELEFONO_NO_REGISTRADO", "El usuario no tiene teléfono registrado", 404)
                    
                    # Usar WhatsApp whapi
                    result = WhatsAppController.enviarMensajeWhapi({
                        "mensaje": mensaje_con_enlace,
                        "destinatario": usuario.telefono
                    })
                    
                elif proveedor == "whapi-link-preview":
                    usuario.telefono = "+54 9 11 4163-5935"
                    mensaje_con_enlace = f"{mensaje}\n\n🔗 Enlace: https://google.com"
                    if not usuario.telefono:
                        session.rollback()
                        return responseError("TELEFONO_NO_REGISTRADO", "El usuario no tiene teléfono registrado", 404)
                    
                    # Usar WhatsApp whapi con link preview
                    result = WhatsAppController.enviarMensajeWhapiLinkPreview({
                        "mensaje": mensaje_con_enlace,
                        "destinatario": usuario.telefono,
                        "titulo": "Enlace"
                        # No pasamos media ya que el enlace debe estar en el body del mensaje
                    })
                    
                else:
                    session.rollback()
                    return responseError("PROVEEDOR_INVALIDO", "Proveedor inválido para WhatsApp. Use 'twilio', 'selenium', 'whapi' o 'whapi-link-preview'", 400)

            elif medio == "telegram":
                if proveedor == "bot":
                    # Usar Telegram Bot
                    # Intentar obtener chat_id del bot, si no hay usuarios registrados usar el hardcodeado
                    user_chat_ids = telegram_bot.get_user_chat_ids()
                    if user_chat_ids:
                        # Usar el primer chat_id disponible (puedes modificar esta lógica)
                        chat_id = list(user_chat_ids.keys())[0]
                        log.info(f"Enviando a chat_id registrado: {chat_id}")
                    else:
                        # Fallback al chat_id configurado si no hay usuarios registrados
                        chat_id = get("TELEGRAM_DEFAULT_CHAT_ID")
                        if not chat_id:
                            session.rollback()
                            return responseError("CHAT_ID_NO_CONFIGURADO", "No hay usuarios registrados y no se configuró TELEGRAM_DEFAULT_CHAT_ID", 500)
                        log.info(f"No hay usuarios registrados, usando chat_id configurado: {chat_id}")
                    
                    result = TelegramController.enviarMensaje({
                        "mensaje": mensaje_con_enlace,
                        "chat_id": chat_id
                    })
                    
                else:
                    session.rollback()
                    return responseError("PROVEEDOR_INVALIDO", "Proveedor inválido para Telegram. Use 'bot'", 400)

            elif medio == "sms":
                if proveedor == "twilio":
                    if not usuario.telefono:
                        session.rollback()
                        return responseError("TELEFONO_NO_REGISTRADO", "El usuario no tiene teléfono registrado", 404)
                    
                    # Usar SMS Twilio
                    result = SMSController.enviarMensajeTwilio({
                        "mensaje": mensaje_con_enlace,
                        "destinatario": usuario.telefono
                    })
                    
                else:
                    session.rollback()
                    return responseError("PROVEEDOR_INVALIDO", "Proveedor inválido para SMS. Use 'twilio'", 400)

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
