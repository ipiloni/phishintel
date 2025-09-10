from flask import jsonify

from app.backend.apis.elevenLabs import elevenLabs
from app.utils.logger import log

class ElevenLabsController:

    @staticmethod
    def generarTTS(data):
        log.info("Se recibio una solicitud para generar TTS: ", data)

        texto = data["texto"]
        idVoz = data["idVoz"]
        estabilidad = data["estabilidad"]
        velocidad = data["velocidad"].strip().lower()

        ttsElevenLabs = elevenLabs.tts(texto, idVoz, estabilidad, velocidad)

        log.info("Finalizo la solicitud")
        return jsonify(ttsElevenLabs)

    @staticmethod
    def generarSTT(ubicacion):
        log.info("Se recibio una solicitud para generar STT: ", ubicacion)
        texto = elevenLabs.stt(ubicacion)
        log.info("Finalizo la solicitud")
        return texto