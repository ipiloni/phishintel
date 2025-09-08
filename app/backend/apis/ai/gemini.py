import google.generativeai as genai

from app.utils.config import get
from app.utils.logger import log

api_key = get("GEMINI_API_KEY_IGNA")

# Configurar la API key una sola vez al inicio
genai.configure(api_key=api_key)

class Gemini:

    @staticmethod
    def generarRespuesta(prompt, conversacion):

        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        try:
            log.info("Se llama a Gemini para generar respuesta")
            response = model.generate_content(
                prompt
                + " " +
                conversacion
            )
            return response

        except Exception as e:
            log.error(e)
            return None