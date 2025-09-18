import re

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
        formato = ""

        if "formato" in data:
            formato = "Quiero que el cuerpo del email sea en formato " + data["formato"]

        if "nivel" in data:
            if data["nivel"] not in [1, 2, 3]:
                contexto = (
                          "Armá un email del estilo Phishing. Necesito que la respuesta que me brindes sea sólamente 'asunto' y 'cuerpo', en formato JSON. El contexto es el siguiente: "
                        + data["contexto"]
                        + ". Supone una escala de dificultad de la simulacion del 1 al 3, siendo 1 el más básico y 3 el más difícil o realista, este email debe generarse con dificultad " + data["nivel"])
            else:
                return responseError("CAMPOS_OBLIGATORIOS", "El campo 'nivel' solo puede tener los valores 1, 2 o 3", 400)

        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
        try:
            response = model.generate_content(
                contexto + ". " + formato,
            )
            return re.sub(r"```(?:json)?", "", response.text).strip(), 201
    
        except Exception as e:
            return responseError("ERROR_API", str(e), 500)

    @staticmethod
    def armarMensaje(data):
        if not data or "contexto" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'contexto'", 400)

        contexto = data["contexto"]
        nivel = data.get("nivel", "Fácil")

        # Construir el prompt para mensaje de WhatsApp
        prompt = f"""Armá un mensaje de WhatsApp del estilo Phishing. 
        El contexto es: {contexto}
        Nivel de dificultad: {nivel}
        
        Necesito que me devuelvas SOLAMENTE el texto del mensaje, sin formato JSON, sin asunto, sin nada más. 
        Solo el contenido del mensaje como si fuera un mensaje de WhatsApp real.
        
        El mensaje debe ser:
        - Conciso (como un mensaje de WhatsApp)
        - Creíble para el nivel de dificultad {nivel}
        - Sin enlaces obvios o sospechosos
        - Con un tono natural y conversacional"""

        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
        try:
            response = model.generate_content(prompt)
            mensaje_texto = response.text.strip()
            
            # Limpiar cualquier formato que pueda haber agregado
            mensaje_texto = re.sub(r"```(?:json)?", "", mensaje_texto).strip()
            mensaje_texto = re.sub(r'^["\']|["\']$', "", mensaje_texto).strip()
            
            return {"mensaje": mensaje_texto}, 201
    
        except Exception as e:
            return responseError("ERROR_API", str(e), 500)

