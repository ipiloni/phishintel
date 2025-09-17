import google.generativeai as genai

from app.utils.config import get
from app.utils.logger import log

api_key = get("GEMINI_API_KEY_IGNA")

# Configurar la API key una sola vez al inicio
genai.configure(api_key=api_key)

class Gemini:

    @staticmethod
    def generarRespuesta(objetivo, conversacion):

        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        try:
            log.info("Se llama a Gemini para generar respuesta")

            # Convertir la conversación a texto
            prompt = ""
            for msg in conversacion:
                rol = msg.get("rol", "").lower()
                contenido = msg.get("mensaje", "").strip()

                if rol == "ia":
                    prompt += f"IA: {contenido}\n"
                elif rol == "destinatario":
                    prompt += f"Usuario: {contenido}\n"

            log.info(f"Conversacion que le enviamos a Gemini: {prompt}")

            # Concatenar con el prompt
            prompt_final = objetivo + "\n" + prompt

            response = model.generate_content(prompt_final)

            textoGenerado = response.candidates[0].content.parts[0].text
            return textoGenerado

        except Exception as e:
            log.error(e)
            return None