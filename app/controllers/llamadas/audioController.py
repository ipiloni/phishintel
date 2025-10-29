from flask import request, jsonify
from datetime import datetime
import os
from app.utils.logger import log
from app.backend.models.error import responseError

class AudioController:
    
    @staticmethod
    def subirAudio():
        """
        Sube un archivo de audio grabado y lo guarda con un nombre descriptivo.
        Retorna la ubicación del archivo para su posterior uso en clonación de voz.
        """
        try:
            # Verificar que se haya enviado un archivo de audio
            if 'audio' not in request.files:
                return responseError("ARCHIVO_FALTANTE", "No se encontró archivo de audio", 400)
            
            audio_file = request.files['audio']
            usuario = request.form.get('usuario', 'Usuario Desconocido')
            area = request.form.get('area', 'Área Desconocida')
            historia = request.form.get('historia', 'Historia no especificada')
            idUsuario = request.form.get('idUsuario', '')
            
            if audio_file.filename == '':
                return responseError("ARCHIVO_VACIO", "No se seleccionó ningún archivo", 400)
            
            # Generar nombre descriptivo para el archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Limpiar nombre de usuario para el filename
            usuario_limpio = usuario.replace(' ', '_').replace('ñ', 'n').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            filename = f"voz_{usuario_limpio}_{timestamp}.mp3"
            
            # Asegurar que la carpeta audios existe
            audio_dir = "./app/audios"
            os.makedirs(audio_dir, exist_ok=True)
            
            # Guardar el archivo
            file_path = os.path.join(audio_dir, filename)
            audio_file.save(file_path)
            
            # Ruta relativa para usar en clonación
            ubicacion_relativa = f"./app/audios/{filename}"
            
            log.info(f"Audio guardado: {filename} - Usuario: {usuario} - Área: {area} - Historia: {historia} - ID Usuario: {idUsuario}")
            
            return jsonify({
                "success": True,
                "message": "Audio guardado correctamente",
                "filename": filename,
                "ubicacion": ubicacion_relativa,
                "usuario": usuario,
                "area": area,
                "historia": historia,
                "idUsuario": idUsuario
            }), 200
            
        except Exception as e:
            log.error(f"Error al subir audio: {str(e)}")
            return responseError("ERROR_INTERNO", f"Error interno del servidor: {str(e)}", 500)
