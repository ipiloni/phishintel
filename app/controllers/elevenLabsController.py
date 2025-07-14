from app.backend.apis.elevenLabs import elevenLabs

class ElevenLabsController:

    @staticmethod
    def generarTTS(texto):
        return elevenLabs.tts(texto)