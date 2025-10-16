from flask import jsonify

from app.backend.apis.elevenLabs import elevenLabs
from app.utils.logger import log

from app.backend.models.error import responseError
from app.controllers.abm.usuariosController import UsuariosController


class ElevenLabsController:

    @staticmethod
    def generarTTS(data):
        log.info("Se recibio una solicitud para generar TTS: ", data)

        modelId = data["modelo"]
        texto = data["texto"]
        idVoz = data["idVoz"]
        estabilidad = data["estabilidad"]
        velocidad = data["velocidad"]
        exageracion = data["exageracion"]

        ttsElevenLabs = elevenLabs.tts(texto, idVoz, modelId, estabilidad, velocidad, exageracion)

        log.info("Finalizo la solicitud")
        return jsonify(ttsElevenLabs)

    @staticmethod
    def generarSTT(ubicacion):
        log.info("Se recibio una solicitud para generar STT: ", ubicacion)
        texto = elevenLabs.stt(ubicacion)
        log.info("Finalizo la solicitud")
        return texto

    @staticmethod
    def clonarVoz(data):
        log.info("Se comienza la clonacion de voz")
        idUsuario = data["idUsuario"]
        ubicacionArchivo = data["ubicacionArchivo"]
        if idUsuario is None:
            log.warn("No se ha especificado el usuario")
            return responseError("USUARIO_INDEFINIDO", f"No se ha especificado el usuario",400)
        if ubicacionArchivo is None:
            log.warn("No se ha especificado el archivo de voz")
            return responseError("ARCHIVO_DE_VOZ_INDEFINIDO", f"No se ha especificado el archivo de voz", 400)
        response, status_code = UsuariosController.obtenerUsuario(idUsuario)
        if status_code != 200:
           log.error(f"No se encontró el usuario")
           return responseError("USUARIO_NO_ENCONTRADO", f"No se ha encontrado el usuario de ID:{idUsuario}", 404)
        from app.apis import exponerAudio
        exponerAudio(f"{ubicacionArchivo}")# expone el archivo .mp3 a internet para que Twilio pueda reproducirlo
        usuario_data = response.get_json()
        idVoz = elevenLabs.clonarVoz(ubicacionArchivo, usuario_data["nombreUsuario"])
        dataUsuario = {"idVoz": idVoz}
        UsuariosController.editarUsuario(idUsuario, dataUsuario)
        log.info("La voz se ha creado correctamente")
        return jsonify({"idVoz": idVoz})