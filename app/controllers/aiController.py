import google.generativeai as genai
from pydantic import BaseModel
from app.utils.config import get
from app.backend.models.error import responseError

class Email(BaseModel):
    asunto: str
    cuerpo: str

api_key = get("GEMINI_API_KEY_IGNA")

# Configurar la API key una sola vez al inicio
genai.configure(api_key=api_key)

class AIController:

    @staticmethod
    def armarEmailGemini(data):
        if not data or "contexto" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'contexto'", 400)

        model = genai.GenerativeModel(model_name="gemini-1.5-flash")  # o gemini-pro, etc.

        try:
            response = model.generate_content(
                data["contexto"]
            )
            return response.text, 201
        except Exception as e:
            return responseError("ERROR_API", str(e), 500)
