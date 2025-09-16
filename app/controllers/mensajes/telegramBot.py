import asyncio
import threading
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.utils.logger import log
from app.utils.config import get
from flask import jsonify

class BotTelegram:
    def __init__(self):
        self.token = get("TELEGRAM_TOKEN")
        self.app = None
        self.is_running = False
        self.user_chat_ids = {}  # Diccionario para almacenar chat_ids de usuarios

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
        
        log.info(f"Usuario conectado - Chat ID: {chat_id}, Username: {user_info.username}, Nombre: {user_info.first_name}")
        
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

    async def start_bot(self):
        """Inicia el bot de Telegram"""
        if self.is_running:
            log.warning("El bot ya está ejecutándose")
            return {"mensaje": "El bot ya está ejecutándose", "status": "running"}

        try:
            # Crear la aplicación
            self.app = Application.builder().token(self.token).build()
            
            # Agregar handlers
            self.app.add_handler(CommandHandler("start", self.start_command))
            self.app.add_handler(CommandHandler("chatid", self.get_chat_id_command))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Iniciar el bot en un hilo separado
            def run_bot():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.app.run_polling())
            
            bot_thread = threading.Thread(target=run_bot, daemon=True)
            bot_thread.start()
            
            self.is_running = True
            log.info("Bot de Telegram iniciado correctamente")
            
            return {
                "mensaje": "Bot de Telegram iniciado correctamente",
                "status": "started",
                "usuarios_registrados": len(self.user_chat_ids)
            }
            
        except Exception as e:
            log.error(f"Error al iniciar el bot: {str(e)}")
            return {"mensaje": f"Error al iniciar el bot: {str(e)}", "status": "error"}

    async def stop_bot(self):
        """Detiene el bot de Telegram"""
        if not self.is_running:
            return {"mensaje": "El bot no está ejecutándose", "status": "stopped"}
        
        try:
            if self.app:
                await self.app.stop()
            self.is_running = False
            log.info("Bot de Telegram detenido")
            return {"mensaje": "Bot de Telegram detenido correctamente", "status": "stopped"}
        except Exception as e:
            log.error(f"Error al detener el bot: {str(e)}")
            return {"mensaje": f"Error al detener el bot: {str(e)}", "status": "error"}

    def get_status(self):
        """Retorna el estado actual del bot"""
        return {
            "is_running": self.is_running,
            "usuarios_registrados": len(self.user_chat_ids),
            "usuarios": self.user_chat_ids
        }

# Instancia global del bot
telegram_bot = BotTelegram()
