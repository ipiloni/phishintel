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
            # Convertir nivel de string a número si es necesario
            nivel = data["nivel"]
            if isinstance(nivel, str):
                nivel_map = {"Fácil": 1, "Medio": 2, "Difícil": 3}
                nivel = nivel_map.get(nivel, 1)
            
            if nivel not in [1, 2, 3]:
                return responseError("CAMPOS_OBLIGATORIOS", "El campo 'nivel' solo puede tener los valores 1, 2 o 3", 400)
            
            contexto = (
                      "Armá un email del estilo Phishing. Necesito que la respuesta que me brindes sea sólamente 'asunto' y 'cuerpo', en formato JSON. El contexto es el siguiente: "
                    + data["contexto"]
                    + ". Supone una escala de dificultad de la simulacion del 1 al 3, siendo 1 el más básico y 3 el más difícil o realista, este email debe generarse con dificultad " + str(nivel))

        try:
            response = AIController.enviarPrompt(contexto + ". " + formato, modelAI)

            return re.sub(r"```(?:json)?", "", response.text).strip(), 201
    
        except Exception as e:
            return responseError("ERROR_API", str(e), 500)

    @staticmethod
    def obtenerInfoLinkedinUsuario(id_usuario):
        """
        Obtiene información completa de LinkedIn de un usuario si tiene perfil cargado
        Realiza web scraping con Selenium para extraer: experiencia, educación, certificaciones, etc.
        """
        from app.config.db_config import SessionLocal
        from app.backend.models import Usuario
        
        session = SessionLocal()
        try:
            usuario = session.query(Usuario).filter_by(idUsuario=id_usuario).first()
            if not usuario or not usuario.perfilLinkedin:
                return None
            
            log.info(f"Extrayendo información de LinkedIn para usuario {id_usuario}")
            
            # Importar funciones de web scraping (las tendremos en el controlador)
            from app.controllers.linkedin_scraper import LinkedinScraper
            
            scraper = LinkedinScraper()
            info_linkedin = scraper.extraer_info_completa(usuario.perfilLinkedin)
            
            if info_linkedin:
                log.info(f"Info de LinkedIn extraída exitosamente para usuario {id_usuario}")
                return info_linkedin
            else:
                log.warning(f"No se pudo extraer info de LinkedIn para usuario {id_usuario}")
                return None
            
        except Exception as e:
            log.error(f"Error obteniendo info de LinkedIn: {str(e)}")
            return None
        finally:
            session.close()

    @staticmethod
    def construirContextoConLinkedin(contexto_base, info_linkedin):
        """
        Construye un contexto enriquecido con información de LinkedIn
        """
        if not info_linkedin:
            return contexto_base
        
        # Construir string con toda la información de LinkedIn
        info_str = "\n\n===== INFORMACIÓN PROFESIONAL DEL DESTINATARIO (LinkedIn) =====\n"
        
        # Información personal
        info_personal = info_linkedin.get("informacion_personal", {})
        if info_personal.get("nombre"):
            info_str += f"- Nombre completo: {info_personal['nombre']}\n"
        if info_personal.get("titulo"):
            info_str += f"- Título profesional: {info_personal['titulo']}\n"
        if info_personal.get("ubicacion"):
            info_str += f"- Ubicación: {info_personal['ubicacion']}\n"
        if info_personal.get("acerca_de"):
            info_str += f"- Acerca de: {info_personal['acerca_de'][:200]}...\n"
        
        # Experiencia
        experiencias = info_linkedin.get("experiencia", [])
        if experiencias:
            info_str += f"\n- Experiencia profesional ({len(experiencias)} trabajos):\n"
            for exp in experiencias[:3]:  # Solo las 3 más recientes
                if exp.get("empresa"):
                    info_str += f"  • {exp.get('titulo', 'N/A')} en {exp['empresa']}"
                    if exp.get("fechas"):
                        info_str += f" ({exp['fechas']})"
                    info_str += "\n"
        
        # Educación
        educaciones = info_linkedin.get("educacion", [])
        if educaciones:
            info_str += f"\n- Educación ({len(educaciones)} estudios):\n"
            for edu in educaciones[:2]:  # Solo las 2 más recientes
                if edu.get("institucion"):
                    info_str += f"  • {edu.get('grado', 'N/A')} - {edu['institucion']}"
                    if edu.get("fechas"):
                        info_str += f" ({edu['fechas']})"
                    info_str += "\n"
        
        # Certificaciones
        certificaciones = info_linkedin.get("licencias_certificaciones", [])
        if certificaciones:
            info_str += f"\n- Certificaciones ({len(certificaciones)}):\n"
            for cert in certificaciones[:2]:  # Solo las 2 más recientes
                if cert.get("nombre"):
                    info_str += f"  • {cert['nombre']}"
                    if cert.get("organizacion"):
                        info_str += f" - {cert['organizacion']}"
                    info_str += "\n"
        
        info_str += "\nUsa esta información para personalizar el email y hacerlo más creíble y relevante para esta persona, tene en cuenta que esta informacion cuenta con info pasada de la persona, ya sea lugares donde trabajo o estudio previamente. Por lo tanto por favor tene en cuenta las fechas de sus trabajos y estudios, y si vas a usar fechas dentro del asunto del mail, como por ejemplo para solicitar un archivo antes de tal fecha, por favor usa la fecha real actual, no tomes una fecha de la info de linkedin."
        info_str += "\nMenciona detalles profesionales específicos si son relevantes para el contexto del phishing.\n"
        
        return contexto_base + info_str

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
            log.warning(f"Hubo un error al intentar obtener la respuesta: {str(ex)}, posiblemente no hay mas creditos de Google, cambiando el API_KEY...")
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

    @staticmethod
    def analizarConversacionLlamada(objetivoActual, conversacionActual):
        prompt = f"""
        Analizá la siguiente conversación. Tu deber es retornar sólamente la palabra 'true' si la conversación cumplió el objetivo; caso contrario retorna 'false'.
        Para saber si la conversación cumplió el objetivo, tenés que basarte en el siguiente criterio: El objetivo se considera cumplido si en la conversación la IA nombra o referencia algo similar o parecido al objetivo.
        El objetivo de esta llamada fue el siguiente: '{objetivoActual}'.
        La conversación resultó ser la siguiente, en formato JSON: {conversacionActual}.
        Recordá sólamente responder con 'true' o 'false'.
        """
        response = AIController.enviarPrompt(prompt, modelAI)

        if response.text == "true":
            return True
        else:
            return False