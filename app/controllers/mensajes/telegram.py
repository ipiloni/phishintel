import asyncio
import threading
import requests
import os
from datetime import datetime

from flask import jsonify
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Bot
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

from app.backend.models.error import responseError
from app.utils.logger import log
from app.config.db_config import SessionLocal
from app.backend.models.telethonSession import TelethonSession


class TelegramController:
    
    def __init__(self):
        self.token = os.environ.get("TELEGRAM_TOKEN")
        self.app = None
        self.is_running = False
        self.user_chat_ids = {}  # Diccionario para almacenar chat_ids de usuarios
        self.bot_thread = None  # Referencia al hilo del bot
        self.loop = None  # Referencia al event loop del bot
        self._stop_event = threading.Event()  # Evento para señalar la detención del hilo

    async def start_command(self, update, context):
        """Maneja el comando /start del bot"""
        chat_id = update.message.chat_id
        user_info = update.effective_user

        # Almacenar información del usuario
        self.user_chat_ids[chat_id] = {
            'username': user_info.username,
            'first_name': user_info.first_name,
            'last_name': user_info.last_name,
            'phone_number': getattr(user_info, 'phone_number', None)
        }

        log.info(
            f"Usuario conectado - Chat ID: {chat_id}, Username: {user_info.username}, Nombre: {user_info.first_name}")

        await update.message.reply_text(
            f"¡Hola {user_info.first_name}! 👋\n\n"
            f"Tu Chat ID es: `{chat_id}`\n\n"
            f"Este bot está configurado para recibir mensajes de PhishIntel. "
            f"Tu información ha sido registrada en el sistema.",
            parse_mode='Markdown'
        )

    async def handle_message(self, update, context):
        """Maneja mensajes de texto normales"""
        chat_id = update.message.chat_id
        message_text = update.message.text

        log.info(f"Mensaje recibido de Chat ID {chat_id}: {message_text}")

        await update.message.reply_text(
            f"Recibí tu mensaje: '{message_text}'\n\n"
            f"Tu Chat ID: `{chat_id}`\n"
            f"Usa /start para registrarte en el sistema.",
            parse_mode='Markdown'
        )

    async def get_chat_id_command(self, update, context):
        """Comando personalizado para obtener el chat_id"""
        chat_id = update.message.chat_id
        await update.message.reply_text(f"Tu Chat ID es: `{chat_id}`", parse_mode='Markdown')

    def get_user_chat_ids(self):
        """Retorna la lista de chat_ids registrados"""
        return self.user_chat_ids

    def get_chat_id_by_username(self, username):
        """Busca un chat_id por username"""
        for chat_id, user_info in self.user_chat_ids.items():
            if user_info.get('username') == username:
                return chat_id
        return None

    def start_bot(self):
        """Inicia el bot de Telegram"""
        if self.is_running:
            log.warning("El bot ya está ejecutándose")
            return jsonify({"mensaje": "El bot ya está ejecutándose", "status": "running"})

        try:
            # Crear la aplicación
            self.app = Application.builder().token(self.token).build()

            # Agregar handlers
            self.app.add_handler(CommandHandler("start", self.start_command))
            self.app.add_handler(CommandHandler("chatid", self.get_chat_id_command))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

            # Iniciar el bot en un hilo separado
            def run_bot():
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
                try:
                    log.debug("Iniciando run_polling...")
                    self.app.run_polling(poll_interval=1.0, timeout=5, stop_signals=None)
                except Exception as e:
                    log.error(f"Error en el hilo del bot: {str(e)}", exc_info=True)
                finally:
                    if self.app:
                        try:
                            self.loop.run_until_complete(self.app.stop())
                            log.info("Aplicación de Telegram detenida")
                            self.loop.run_until_complete(self.app.shutdown())
                            log.info("Aplicación de Telegram cerrada completamente")
                        except Exception as e:
                            log.warning(f"No se pudo ejecutar stop/shutdown: {str(e)}", exc_info=True)
                    if not self.loop.is_closed():
                        try:
                            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
                            self.loop.close()
                            log.info("Event loop cerrado")
                        except Exception as e:
                            log.warning(f"No se pudo cerrar el event loop: {str(e)}", exc_info=True)
                    log.info("Hilo del bot terminado")
                    self._stop_event.set()  # Señalar terminación

            self._stop_event.clear()  # Asegurar que el evento de detención esté limpio
            self.bot_thread = threading.Thread(target=run_bot, daemon=True)
            self.bot_thread.start()

            self.is_running = True
            log.info("Bot de Telegram iniciado correctamente")

            return jsonify({
                "mensaje": "Bot de Telegram iniciado correctamente",
                "status": "started",
                "usuarios_registrados": len(self.user_chat_ids)
            })

        except Exception as e:
            log.error(f"Error al iniciar el bot: {str(e)}", exc_info=True)
            self.is_running = False
            self.app = None
            self.bot_thread = None
            self.loop = None
            return jsonify({"mensaje": f"Error al iniciar el bot: {str(e)}", "status": "error"})

    def stop_bot(self):
        """Detiene el bot de Telegram"""
        if not self.is_running:
            log.warning("El bot no está ejecutándose")
            return jsonify({"mensaje": "El bot no está ejecutándose", "status": "stopped"})

        try:
            log.info("Iniciando detención del bot de Telegram...")
            log.debug(
                f"Estado inicial - Hilo vivo: {self.bot_thread.is_alive() if self.bot_thread else False}, Loop cerrado: {self.loop.is_closed() if self.loop else True}")

            # Programar la detención en el event loop del bot
            if self.app and self.loop and not self.loop.is_closed():
                log.info("Programando detención del polling en el loop del bot...")
                future = asyncio.run_coroutine_threadsafe(self.app.updater.stop(), self.loop)
                future.result(timeout=10.0)  # Esperar hasta 10s por la detención

            # Esperar a que el hilo termine
            if self.bot_thread and self.bot_thread.is_alive():
                log.info("Esperando a que el hilo del bot termine...")
                self.bot_thread.join(timeout=30.0)  # Timeout aumentado
                if self.bot_thread.is_alive():
                    log.warning("El hilo del bot no terminó en el tiempo esperado - posible hang en network")
                else:
                    log.info("Hilo del bot ha terminado exitosamente")

            # Limpiar referencias
            self.app = None
            self.bot_thread = None
            self.loop = None
            self.is_running = False

            log.info("Bot de Telegram detenido completamente")
            return jsonify({"mensaje": "Bot de Telegram detenido correctamente", "status": "stopped"})

        except Exception as e:
            log.error(f"Error al detener el bot: {str(e)}", exc_info=True)
            self.app = None
            self.bot_thread = None
            self.loop = None
            self.is_running = False
            return jsonify({"mensaje": f"Error al detener el bot: {str(e)}", "status": "error"})

    def get_status(self):
        """Retorna el estado actual del bot"""
        return jsonify({
            "is_running": self.is_running,
            "usuarios_registrados": len(self.user_chat_ids),
            "usuarios": self.user_chat_ids
        })

    @staticmethod
    def enviarMensaje(data):
        """
        Envía un mensaje de Telegram usando el bot.
        
        Args:
            data (dict): Diccionario con los siguientes campos:
                - mensaje (str): Mensaje a enviar
                - chat_id (str, opcional): Chat ID del destinatario
                
        Returns:
            tuple: (response, status_code)
        """
        log.info("Se recibió una solicitud para enviar mensaje via Telegram")

        if not data or "mensaje" not in data:
            log.warn("Falta el campo obligatorio 'mensaje'")
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'mensaje'", 400)

        mensaje = data["mensaje"]
        chat_id = data.get("chat_id")

        try:
            # Obtener el token desde las variables de entorno
            token = os.environ.get("TELEGRAM_TOKEN")
            if not token:
                log.error("Token de Telegram no configurado")
                return responseError("TOKEN_NO_CONFIGURADO", "Token de Telegram no configurado", 500)

            # Si no se proporciona chat_id, usar el configurado como fallback
            if not chat_id:
                chat_id = os.environ.get("TELEGRAM_DEFAULT_CHAT_ID")
                if not chat_id:
                    log.error("No se proporcionó chat_id y no se configuró TELEGRAM_DEFAULT_CHAT_ID")
                    return responseError("CHAT_ID_NO_CONFIGURADO", "No se proporcionó chat_id y no se configuró TELEGRAM_DEFAULT_CHAT_ID", 400)
                log.info(f"No se proporcionó chat_id, usando configurado: {chat_id}")

            # Crear el bot
            bot = Bot(token=token)
            
            # Enviar mensaje via Telegram (usando asyncio para manejar la función async)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(bot.send_message(chat_id=chat_id, text=mensaje))
            loop.close()
            
            log.info(f"Mensaje de Telegram enviado a {chat_id}")
            
            return jsonify({
                "mensaje": "Mensaje enviado correctamente via Telegram",
                "chat_id": chat_id,
                "contenido": mensaje
            }), 201

        except Exception as e:
            error_msg = f"Error al enviar mensaje via Telegram: {str(e)}"
            log.error(error_msg)
            return responseError("ERROR_TELEGRAM", error_msg, 500)

    @staticmethod
    def enviarMensajeHTML(data):
        """
        Envía un mensaje de Telegram usando el bot con formato HTML.
        Permite enviar enlaces clickeables y otros elementos HTML.
        
        Args:
            data (dict): Diccionario con los siguientes campos:
                - mensaje (str): Mensaje a enviar (puede contener HTML)
                - chat_id (str, opcional): Chat ID del destinatario
                
        Returns:
            tuple: (response, status_code)
        """
        log.info("Se recibió una solicitud para enviar mensaje HTML via Telegram")

        if not data or "mensaje" not in data:
            log.warn("Falta el campo obligatorio 'mensaje'")
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'mensaje'", 400)

        mensaje = data["mensaje"]
        chat_id = data.get("chat_id")

        try:
            # Obtener el token desde las variables de entorno
            token = os.environ.get("TELEGRAM_TOKEN")
            if not token:
                log.error("Token de Telegram no configurado")
                return responseError("TOKEN_NO_CONFIGURADO", "Token de Telegram no configurado", 500)

            # Si no se proporciona chat_id, usar el configurado como fallback
            if not chat_id:
                chat_id = os.environ.get("TELEGRAM_DEFAULT_CHAT_ID")
                if not chat_id:
                    log.error("No se proporcionó chat_id y no se configuró TELEGRAM_DEFAULT_CHAT_ID")
                    return responseError("CHAT_ID_NO_CONFIGURADO", "No se proporcionó chat_id y no se configuró TELEGRAM_DEFAULT_CHAT_ID", 400)
                log.info(f"No se proporcionó chat_id, usando configurado: {chat_id}")

            # Crear el bot
            bot = Bot(token=token)
            
            # Enviar mensaje via Telegram con formato HTML (usando asyncio para manejar la función async)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(bot.send_message(chat_id=chat_id, text=mensaje, parse_mode="HTML"))
            loop.close()
            
            log.info(f"Mensaje HTML de Telegram enviado a {chat_id}")
            
            return jsonify({
                "mensaje": "Mensaje HTML enviado correctamente via Telegram",
                "chat_id": chat_id,
                "contenido": mensaje
            }), 201

        except Exception as e:
            error_msg = f"Error al enviar mensaje HTML via Telegram: {str(e)}"
            log.error(error_msg)
            return responseError("ERROR_TELEGRAM", error_msg, 500)

    @staticmethod
    def _obtenerClienteTelethon():
        """
        Obtiene un cliente Telethon configurado desde la sesión guardada en BD.
        
        Returns:
            TelegramClient o None si no hay sesión válida
        """
        api_id = get("TELEGRAM_APP_ID")
        api_hash = get("TELEGRAM_API_HASH")
        
        if not api_id or not api_hash:
            log.error("TELEGRAM_APP_ID o TELEGRAM_API_HASH no configurados")
            return None
        
        try:
            session_db = SessionLocal()
            try:
                # Buscar sesión activa en BD
                session_record = session_db.query(TelethonSession).filter_by(estaActiva=True).first()
                
                if not session_record or not session_record.sessionData:
                    log.warn("No hay sesión de Telethon activa en BD")
                    return None
                
                # Crear StringSession desde datos de BD
                session_string = session_record.sessionData.decode('utf-8')
                session = StringSession(session_string)
                
                # Crear cliente con configuración DC 2
                client = TelegramClient(
                    session,
                    int(api_id),
                    api_hash,
                    connection_retries=3,
                    retry_delay=1,
                    timeout=10
                )
                
                log.info("Cliente Telethon creado desde sesión de BD")
                return client
                
            finally:
                session_db.close()
                
        except Exception as e:
            log.error(f"Error al obtener cliente Telethon: {str(e)}")
            return None
    
    @staticmethod
    def enviarMensajeTelethon(data):
        """
        Envía un mensaje SMS usando Telethon (cuenta propia de Telegram).
        
        Args:
            data (dict): Diccionario con los siguientes campos:
                - mensaje (str): Mensaje a enviar (puede contener HTML)
                - destinatario (str): Número de teléfono del destinatario
                
        Returns:
            tuple: (response, status_code)
        """
        log.info("Se recibió una solicitud para enviar mensaje via Telegram con Telethon")

        if not data or "mensaje" not in data or "destinatario" not in data:
            log.warn("Faltan campos obligatorios")
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios (mensaje o destinatario)", 400)

        mensaje = data["mensaje"]
        destinatario = data["destinatario"]

        try:
            # Obtener cliente Telethon
            client = TelegramController._obtenerClienteTelethon()
            
            if not client:
                return responseError(
                    "SESION_NO_CONFIGURADA",
                    "No hay sesión de Telethon activa. Por favor, autentícate primero usando el endpoint /api/telegram/telethon/auth",
                    401
                )
            
            # Conectar cliente si no está conectado
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                if not client.is_connected():
                    loop.run_until_complete(client.connect())
                
                # Verificar si está autorizado
                if not loop.run_until_complete(client.is_user_authorized()):
                    return responseError(
                        "SESION_NO_AUTORIZADA",
                        "La sesión de Telethon no está autorizada. Por favor, autentícate nuevamente usando el endpoint /api/telegram/telethon/auth",
                        401
                    )
                
                # Enviar mensaje
                # Telethon requiere que el número esté en contactos o buscar el usuario primero
                try:
                    # Normalizar el número - Remover el 9 después del código de país para Argentina
                    phone_normalized = destinatario
                    if not phone_normalized.startswith('+'):
                        phone_normalized = '+' + phone_normalized
                    
                    # Si es un número argentino con formato +549, remover el 9 para que coincida con contactos
                    # Formato BD: +5491141635935 -> Formato Telegram: +541141635935
                    if phone_normalized.startswith('+549') and len(phone_normalized) > 4:
                        # Remover el 9 después de +54
                        phone_normalized = '+54' + phone_normalized[4:]
                        log.info(f"Número normalizado de {destinatario} a {phone_normalized} (removido 9 móvil)")
                    
                    # Intentar enviar directamente primero
                    try:
                        loop.run_until_complete(
                            client.send_message(phone_normalized, mensaje, parse_mode='HTML')
                        )
                    except ValueError as e:
                        # Si falla porque no encuentra la entidad, intentar agregar como contacto
                        if "Cannot find any entity" in str(e) or "entity" in str(e).lower():
                            log.info(f"Usuario {phone_normalized} no encontrado, intentando agregar como contacto")
                            
                            # Agregar contacto temporalmente
                            contact = InputPhoneContact(
                                client_id=0,
                                phone=phone_normalized,
                                first_name="Usuario",
                                last_name="PhishIntel"
                            )
                            
                            result = loop.run_until_complete(
                                client(ImportContactsRequest([contact]))
                            )
                            
                            # Intentar enviar nuevamente después de agregar contacto
                            loop.run_until_complete(
                                client.send_message(phone_normalized, mensaje, parse_mode='HTML')
                            )
                        else:
                            raise
                    
                except Exception as send_error:
                    error_msg = f"Error al enviar mensaje: {str(send_error)}"
                    log.error(error_msg)
                    raise
                
                log.info(f"Mensaje Telethon enviado a {destinatario}")
                
                return jsonify({
                    "mensaje": "Mensaje enviado correctamente via Telethon",
                    "destinatario": destinatario,
                    "contenido": mensaje
                }), 201
                
            finally:
                # Desconectar el cliente correctamente antes de cerrar el loop
                try:
                    if client.is_connected():
                        # Desconectar y esperar a que termine
                        loop.run_until_complete(client.disconnect())
                        # Dar un pequeño delay para que las tareas se cancelen apropiadamente
                        import time
                        time.sleep(0.5)
                except Exception as disconnect_error:
                    log.warn(f"Error al desconectar cliente Telethon: {str(disconnect_error)}")
                finally:
                    # Cerrar todas las tareas pendientes antes de cerrar el loop
                    try:
                        # Cancelar todas las tareas pendientes
                        pending = asyncio.all_tasks(loop)
                        for task in pending:
                            task.cancel()
                        # Esperar a que se cancelen
                        if pending:
                            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    except Exception as task_error:
                        log.warn(f"Error al cancelar tareas: {str(task_error)}")
                    finally:
                        loop.close()
                
        except Exception as e:
            error_msg = f"Error al enviar mensaje via Telethon: {str(e)}"
            log.error(error_msg)
            return responseError("ERROR_TELETHON", error_msg, 500)
    
    @staticmethod
    def autenticarTelethon(data):
        """
        Maneja el flujo de autenticación de Telethon en etapas.
        
        Args:
            data (dict): Diccionario con campos opcionales:
                - phone (str): Número de teléfono
                - code (str): Código de verificación recibido
                - password (str): Contraseña 2FA (si aplica)
                
        Returns:
            tuple: (response, status_code)
        """
        log.info("Se recibió solicitud de autenticación Telethon")
        
        api_id = os.environ.get("TELEGRAM_APP_ID")
        api_hash = os.environ.get("TELEGRAM_API_HASH")
        
        if not api_id or not api_hash:
            return responseError(
                "CREDENCIALES_NO_CONFIGURADAS",
                "TELEGRAM_APP_ID o TELEGRAM_API_HASH no configurados en properties.env",
                500
            )
        
        phone = data.get("phone")
        code = data.get("code")
        password = data.get("password")
        
        try:
            # Crear cliente temporal para autenticación
            temp_session = StringSession()
            client = TelegramClient(
                temp_session,
                int(api_id),
                api_hash,
                connection_retries=3,
                retry_delay=1,
                timeout=10
            )
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Conectar cliente
                loop.run_until_complete(client.connect())
                
                # Etapa 1: Enviar teléfono
                if phone and not code and not password:
                    if not phone.startswith('+'):
                        phone = '+' + phone
                    
                    # Enviar código y obtener phone_code_hash
                    result = loop.run_until_complete(client.send_code_request(phone))
                    phone_code_hash = result.phone_code_hash
                    
                    # Guardar solo los datos necesarios (NO el cliente)
                    session_string = temp_session.save()
                    
                    # Guardar estado en BD para persistencia
                    TelegramController._guardarEstadoAuthEnBD(phone, phone_code_hash, session_string)
                    
                    # También guardar en memoria por si acaso
                    _telethon_auth_state['phone'] = phone
                    _telethon_auth_state['session_string'] = session_string
                    _telethon_auth_state['phone_code_hash'] = phone_code_hash
                    
                    # Desconectar y cerrar el cliente
                    try:
                        if client.is_connected():
                            loop.run_until_complete(client.disconnect())
                    except Exception as e:
                        log.warn(f"Error al desconectar cliente: {str(e)}")
                    finally:
                        loop.close()
                    
                    log.info(f"Código de verificación enviado a {phone}")
                    
                    return jsonify({
                        "status": "code_sent",
                        "message": f"Código de verificación enviado a {phone}. Por favor, envía el código recibido.",
                        "phone": phone
                    }), 200
                
                # Etapa 2: Verificar código
                if phone and code and not password:
                    # Normalizar el teléfono antes de comparar
                    if not phone.startswith('+'):
                        phone = '+' + phone
                    
                    # Intentar obtener estado de memoria primero, si no de BD
                    stored_phone = _telethon_auth_state.get('phone')
                    stored_hash = _telethon_auth_state.get('phone_code_hash')
                    stored_session_string = _telethon_auth_state.get('session_string')
                    
                    # Si no hay estado en memoria, intentar cargar desde BD
                    if not stored_phone or not stored_hash or not stored_session_string:
                        estado_bd = TelegramController._obtenerEstadoAuthDesdeBD()
                        if estado_bd:
                            stored_phone = estado_bd.get('phone')
                            stored_hash = estado_bd.get('phone_code_hash')
                            stored_session_string = estado_bd.get('session_string')
                            # Actualizar memoria también
                            _telethon_auth_state.update(estado_bd)
                    
                    if stored_phone != phone:
                        loop.close()
                        log.error(f"Teléfono no coincide: almacenado='{stored_phone}', recibido='{phone}'")
                        return responseError(
                            "TELEFONO_NO_COINCIDE",
                            f"El teléfono no coincide con la solicitud anterior. Almacenado: {stored_phone}, Recibido: {phone}",
                            400
                        )
                    
                    if not stored_hash or not stored_session_string:
                        loop.close()
                        return responseError(
                            "ESTADO_PERDIDO",
                            "No se encontró el estado de autenticación. Por favor, inicia el proceso nuevamente.",
                            400
                        )
                    
                    # Crear nuevo cliente desde la sesión guardada (con nuevo event loop)
                    restored_session = StringSession(stored_session_string)
                    restored_client = TelegramClient(
                        restored_session,
                        int(api_id),
                        api_hash,
                        connection_retries=3,
                        retry_delay=1,
                        timeout=10
                    )
                    
                    try:
                        # Conectar con el nuevo event loop
                        loop.run_until_complete(restored_client.connect())
                        
                        # Intentar iniciar sesión con código y hash
                        loop.run_until_complete(
                            restored_client.sign_in(phone, code, phone_code_hash=stored_hash)
                        )
                        
                        # Si llegamos aquí, autenticación exitosa (sin 2FA)
                        final_session_string = restored_session.save()
                        
                        # Guardar sesión en BD
                        TelegramController._guardarSesionEnBD(final_session_string)
                        
                        # Limpiar estado temporal
                        _telethon_auth_state.clear()
                        
                        # Desconectar
                        try:
                            if restored_client.is_connected():
                                loop.run_until_complete(restored_client.disconnect())
                        except Exception as e:
                            log.warn(f"Error al desconectar cliente: {str(e)}")
                        finally:
                            loop.close()
                        
                        log.info("Autenticación Telethon exitosa")
                        
                        return jsonify({
                            "status": "authenticated",
                            "message": "Autenticación exitosa. Sesión guardada."
                        }), 200
                        
                    except SessionPasswordNeededError:
                        # Requiere contraseña 2FA - guardar el cliente actualizado
                        updated_session_string = restored_session.save()
                        _telethon_auth_state['session_string'] = updated_session_string
                        
                        # Actualizar estado en BD
                        TelegramController._actualizarEstadoAuthEnBD(phone, stored_hash, updated_session_string)
                        
                        # Desconectar pero mantener el estado
                        try:
                            if restored_client.is_connected():
                                loop.run_until_complete(restored_client.disconnect())
                        except Exception as e:
                            log.warn(f"Error al desconectar cliente: {str(e)}")
                        finally:
                            loop.close()
                        
                        log.info("Se requiere contraseña 2FA")
                        
                        return jsonify({
                            "status": "password_required",
                            "message": "Se requiere contraseña de autenticación de dos factores. Por favor, envía la contraseña.",
                            "phone": phone
                        }), 200
                    
                    except Exception as e:
                        try:
                            if restored_client.is_connected():
                                loop.run_until_complete(restored_client.disconnect())
                        except Exception as disconnect_error:
                            log.warn(f"Error al desconectar cliente: {str(disconnect_error)}")
                        finally:
                            loop.close()
                        raise
                
                # Etapa 3: Verificar contraseña 2FA
                if phone and code and password:
                    # Normalizar el teléfono antes de comparar
                    if not phone.startswith('+'):
                        phone = '+' + phone
                    
                    # Intentar obtener estado de memoria primero, si no de BD
                    stored_phone = _telethon_auth_state.get('phone')
                    stored_hash = _telethon_auth_state.get('phone_code_hash')
                    stored_session_string = _telethon_auth_state.get('session_string')
                    
                    # Si no hay estado en memoria, intentar cargar desde BD
                    if not stored_phone or not stored_hash or not stored_session_string:
                        estado_bd = TelegramController._obtenerEstadoAuthDesdeBD()
                        if estado_bd:
                            stored_phone = estado_bd.get('phone')
                            stored_hash = estado_bd.get('phone_code_hash')
                            stored_session_string = estado_bd.get('session_string')
                            # Actualizar memoria también
                            _telethon_auth_state.update(estado_bd)
                    
                    if stored_phone != phone:
                        loop.close()
                        log.error(f"Teléfono no coincide: almacenado='{stored_phone}', recibido='{phone}'")
                        return responseError(
                            "TELEFONO_NO_COINCIDE",
                            f"El teléfono no coincide con la solicitud anterior. Almacenado: {stored_phone}, Recibido: {phone}",
                            400
                        )
                    
                    if not stored_hash or not stored_session_string:
                        loop.close()
                        return responseError(
                            "ESTADO_PERDIDO",
                            "No se encontró el estado de autenticación. Por favor, inicia el proceso nuevamente.",
                            400
                        )
                    
                    # Crear nuevo cliente desde la sesión guardada
                    restored_session = StringSession(stored_session_string)
                    restored_client = TelegramClient(
                        restored_session,
                        int(api_id),
                        api_hash,
                        connection_retries=3,
                        retry_delay=1,
                        timeout=10
                    )
                    
                    try:
                        # Conectar con el nuevo event loop
                        loop.run_until_complete(restored_client.connect())
                        
                        loop.run_until_complete(
                            restored_client.sign_in(phone, code, phone_code_hash=stored_hash, password=password)
                        )
                        
                        # Autenticación exitosa con 2FA
                        final_session_string = restored_session.save()
                        
                        # Guardar sesión en BD
                        TelegramController._guardarSesionEnBD(final_session_string)
                        
                        # Limpiar estado temporal
                        _telethon_auth_state.clear()
                        
                        # Desconectar
                        try:
                            if restored_client.is_connected():
                                loop.run_until_complete(restored_client.disconnect())
                        except Exception as e:
                            log.warn(f"Error al desconectar cliente: {str(e)}")
                        finally:
                            loop.close()
                        
                        log.info("Autenticación Telethon exitosa con 2FA")
                        
                        return jsonify({
                            "status": "authenticated",
                            "message": "Autenticación exitosa con 2FA. Sesión guardada."
                        }), 200
                        
                    except Exception as e:
                        try:
                            if restored_client.is_connected():
                                loop.run_until_complete(restored_client.disconnect())
                        except Exception as disconnect_error:
                            log.warn(f"Error al desconectar cliente: {str(disconnect_error)}")
                        finally:
                            loop.close()
                        return responseError(
                            "ERROR_AUTENTICACION",
                            f"Error al verificar contraseña 2FA: {str(e)}",
                            400
                        )
                
                # Si no hay datos suficientes
                loop.close()
                return responseError(
                    "DATOS_INSUFICIENTES",
                    "Proporciona 'phone' para iniciar, luego 'phone' y 'code' para verificar, y 'password' si se requiere 2FA",
                    400
                )
                
            except Exception as e:
                loop.close()
                raise
                
        except Exception as e:
            error_msg = f"Error en autenticación Telethon: {str(e)}"
            log.error(error_msg)
            _telethon_auth_state.clear()
            return responseError("ERROR_TELETHON_AUTH", error_msg, 500)
    
    @staticmethod
    def _guardarEstadoAuthEnBD(phone, phone_code_hash, session_string):
        """
        Guarda el estado de autenticación en proceso en la BD.
        
        Args:
            phone (str): Número de teléfono
            phone_code_hash (str): Hash del código de verificación
            session_string (str): String de sesión temporal
        """
        session_db = SessionLocal()
        try:
            # Limpiar estados anteriores de autenticación
            session_db.query(TelethonSession).filter(
                TelethonSession.sessionData.is_(None)
            ).delete()
            
            # Crear nuevo registro de estado temporal
            estado_auth = TelethonSession(
                phone=phone,
                phoneCodeHash=phone_code_hash,
                tempSessionString=session_string.encode('utf-8'),
                estaActiva=False,  # No está activa hasta completar autenticación
                fechaCreacion=datetime.now(),
                fechaActualizacion=datetime.now()
            )
            
            session_db.add(estado_auth)
            session_db.commit()
            
            log.info(f"Estado de autenticación guardado en BD para {phone}")
            
        except Exception as e:
            session_db.rollback()
            log.error(f"Error al guardar estado de auth en BD: {str(e)}")
            raise
        finally:
            session_db.close()
    
    @staticmethod
    def _obtenerEstadoAuthDesdeBD():
        """
        Obtiene el estado de autenticación en proceso desde la BD.
        
        Returns:
            dict con phone, phone_code_hash, session_string o None
        """
        session_db = SessionLocal()
        try:
            estado = session_db.query(TelethonSession).filter(
                TelethonSession.sessionData.is_(None),
                TelethonSession.phone.isnot(None)
            ).order_by(TelethonSession.fechaCreacion.desc()).first()
            
            if estado and estado.tempSessionString:
                return {
                    'phone': estado.phone,
                    'phone_code_hash': estado.phoneCodeHash,
                    'session_string': estado.tempSessionString.decode('utf-8')
                }
            
            return None
            
        except Exception as e:
            log.error(f"Error al obtener estado de auth desde BD: {str(e)}")
            return None
        finally:
            session_db.close()
    
    @staticmethod
    def _actualizarEstadoAuthEnBD(phone, phone_code_hash, session_string):
        """
        Actualiza el estado de autenticación en BD.
        
        Args:
            phone (str): Número de teléfono
            phone_code_hash (str): Hash del código de verificación
            session_string (str): String de sesión actualizado
        """
        session_db = SessionLocal()
        try:
            estado = session_db.query(TelethonSession).filter(
                TelethonSession.phone == phone,
                TelethonSession.sessionData.is_(None)
            ).first()
            
            if estado:
                estado.tempSessionString = session_string.encode('utf-8')
                estado.phoneCodeHash = phone_code_hash
                estado.fechaActualizacion = datetime.now()
                session_db.commit()
                log.info(f"Estado de autenticación actualizado en BD para {phone}")
            
        except Exception as e:
            session_db.rollback()
            log.error(f"Error al actualizar estado de auth en BD: {str(e)}")
        finally:
            session_db.close()
    
    @staticmethod
    def _guardarSesionEnBD(session_string):
        """
        Guarda la sesión de Telethon autenticada en la base de datos.
        
        Args:
            session_string (str): String de sesión serializado
        """
        session_db = SessionLocal()
        try:
            # Limpiar estados temporales de autenticación
            session_db.query(TelethonSession).filter(
                TelethonSession.sessionData.is_(None)
            ).delete()
            
            # Marcar sesiones anteriores como inactivas
            session_db.query(TelethonSession).filter(
                TelethonSession.sessionData.isnot(None)
            ).update({"estaActiva": False})
            
            # Crear nueva sesión autenticada
            nueva_sesion = TelethonSession(
                sessionData=session_string.encode('utf-8'),
                estaActiva=True,
                fechaCreacion=datetime.now(),
                fechaActualizacion=datetime.now()
            )
            
            session_db.add(nueva_sesion)
            session_db.commit()
            
            log.info("Sesión de Telethon guardada en BD")
            
        except Exception as e:
            session_db.rollback()
            log.error(f"Error al guardar sesión en BD: {str(e)}")
            raise
        finally:
            session_db.close()


# Diccionario para almacenar estado de autenticación en proceso
_telethon_auth_state = {}

# Instancia global del bot
telegram_bot = TelegramController()
