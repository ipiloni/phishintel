from flask import jsonify
from google import genai
from pydantic import BaseModel
from app.utils.config import get
from app.backend.models.error import responseError

class Email(BaseModel):
    asunto: str
    cuerpo: str

api_key = get("GEMINI_API_KEY_IGNA")

class AIController:

    @staticmethod
    def armarEmailGemini(data):
        if not data or "contexto" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'contexto'", 400)

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=data["contexto"],
            config={
                "response_mime_type": "application/json",
                "response_schema": Email,
            }
        )

        return response.text, 201