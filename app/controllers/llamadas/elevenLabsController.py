from app.backend.apis.elevenLabs import elevenLabs
from app.utils.logger import log

class ElevenLabsController:

    @staticmethod
    def generarTTS(data):
        log.info("Se recibio una solicitud para generar TTS: ", data)
        ttsElevenLabs = elevenLabs.tts(data)
        log.info("Finalizo la solicitud")
        return ttsElevenLabs

    @staticmethod
    def generarSTT(ubicacion):
        log.info("Se recibio una solicitud para generar STT: ", ubicacion)
        texto = elevenLabs.stt(ubicacion)
        log.info("Finalizo la solicitud")
        return texto