import re
import google.generativeai as genai
from flask import jsonify

from app.utils.config import get
from app.backend.models.error import responseError
from app.utils.logger import log

api_key_igna = get("GEMINI_API_KEY_IGNA")
api_key_marcos = get("GEMINI_API_KEY_MARCOS")

modelAI = "gemini-2.5-flash"

# Configurar la API key una sola vez al inicio
genai.configure(api_key=api_key_igna)

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

        try:
            response = AIController.enviarPrompt(contexto + ". " + formato, modelAI)

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

        try:

            response = AIController.enviarPrompt(prompt, modelAI)

            mensaje_texto = response.text.strip()
            
            # Limpiar cualquier formato que pueda haber agregado
            mensaje_texto = re.sub(r"```(?:json)?", "", mensaje_texto).strip()
            mensaje_texto = re.sub(r'^["\']|["\']$', "", mensaje_texto).strip()
            
            return {"mensaje": mensaje_texto}, 201
    
        except Exception as e:
            return responseError("ERROR_API", str(e), 500)


    @staticmethod
    def armarMensajeLlamada(objetivo, conversacion):
        """ Esta accion vamos a utilizarla para generar textos de una llamada en tiempo real, debido a que utiliza un modelo de procesamiento rapido """
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

            response = AIController.enviarPrompt(prompt_final, "gemini-2.5-flash-lite")

            textoGenerado = response.candidates[0].content.parts[0].text
            return textoGenerado

        except Exception as ex:
            log.error(f"Hubo un error al llamar a Gemini: {str(ex)}")
            return None

    @staticmethod
    def enviarAGemini(prompt, modeloIA):
        try:

            if modeloIA is None:
                log.info("No se especifico modelo de IA, utilizando predeterminado...")
                modeloIA = "gemini-2.0-flash-lite"

            log.info("Se llama a Gemini...")

            response = AIController.enviarPrompt(prompt, modeloIA)

            textoGenerado = response.candidates[0].content.parts[0].text
            return textoGenerado

        except Exception as e:
            log.error(e)
            return None


    @staticmethod
    def enviarPrompt(prompt, modelo):
        model = genai.GenerativeModel(model_name=modelo)

        try:
            return model.generate_content(prompt)
        except Exception as ex:
            log.warning(
                f"Hubo un error al intentar obtener la respuesta: {str(ex)}, posiblemente no hay mas creditos de Google, cambiando el API_KEY...")
            genai.configure(api_key=api_key_marcos)
            return model.generate_content(prompt)

    @staticmethod
    def crearObjetivoLlamada():
        model = "gemini-2.0-flash-lite"
        log.info("Se llama a Gemini...")

        prompt = ""

        response = AIController.enviarPrompt(prompt, model)

        return jsonify({
            "objetivo": response
        }), 201