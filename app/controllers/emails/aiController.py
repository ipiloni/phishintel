import google.generativeai as genai
from app.utils.config import get
from app.backend.models.error import responseError

api_key = get("GEMINI_API_KEY_IGNA")

# Configurar la API key una sola vez al inicio
genai.configure(api_key=api_key)

# GEMINI 1.5 FLASH es la MAS RAPIDA. Nos va a servir para las cosas en vivo. Quizas para emails y demas podemos usar una mas eficaz.

class AIController:

    @staticmethod
    def armarEmail(data):
        if not data or "contexto" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'contexto'", 400)

        contexto = data["contexto"]

        if "nivel" in data:
            if data["nivel"] not in [1, 2, 3]:
                contexto = data["contexto"] + ". Imagina una escala de dificultad de la simulacion del 1 al 3, este email debe generarse con dificultad " + data["nivel"]
            else:
                return responseError("CAMPOS_OBLIGATORIOS", "El campo 'nivel' solo puede tener los valores 1, 2 o 3", 400)

        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        try:
            response = model.generate_content(
                contexto
            )
            return response.text, 201
        except Exception as e:
            return responseError("ERROR_API", str(e), 500)

    # @staticmethod
    # def armarMensaje(data):
    #     if not data or "contexto" not in data:
    #         return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'contexto'", 400)
    #
    #