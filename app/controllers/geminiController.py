from bs4 import BeautifulSoup
from flask import jsonify

from app.backend.apis.ai.gemini import Gemini
from app.backend.models.error import responseError
from app.utils.config import get
from app.utils.logger import log
import requests

API_KEY = get("API_KEY_WEB_SCRAPPING_IGNA")
CX = get("CX_WEB_SCRAPPING_IGNA")

class GeminiController:

    @staticmethod
    def generarWebScrapping(idLinkedin):
        perfil_url = GeminiController.buscarPerfilLinkedin(idLinkedin)
        if not perfil_url:
            log.error(f"No se encontro el perfil: {idLinkedin}")
            return responseError("ERROR_API", "No se encontro el perfil del Linkedin con la API de Google", 404)

        info = GeminiController.extraerInfoPublica(perfil_url)
        return jsonify({
            "perfil_url": perfil_url,
            "educacion": info.get("educacion", []),
            "experiencia": info.get("experiencia", [])
        })

    @staticmethod
    def buscarPerfilLinkedin(idLinkedin):

        log.info("Se recibe una solicitud para generar web scrapping")
        """Usa la Google Custom Search API para encontrar la URL completa del perfil LinkedIn"""
        query = f"site:linkedin.com/in {idLinkedin}"
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": API_KEY,
            "cx": CX,
            "q": query
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            if items:
                # Retornamos la primera URL encontrada
                return items[0]["link"]
            else:
                return None
        else:
            log.error(f"Error en la API de Google: {response.status_code} - {response.text}")
            return responseError("ERROR_API",f"Error en la API de Google: {response.status_code} - {response.text}", 500)

    @staticmethod
    def extraerInfoPublica(url):
        """Scrapea información pública visible del perfil"""
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get(url, headers=headers)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            educacion = []
            experiencia = []

            # Esto es orientativo; LinkedIn cambia el HTML seguido
            for section in soup.find_all(["section", "div"]):
                text = section.get_text(strip=True)
                if "Educación" in text:
                    educacion.append(text)
                if "Experiencia" in text:
                    experiencia.append(text)

            return {"educacion": educacion, "experiencia": experiencia}
        else:
            log.error(f"No se pudo acceder al perfil: {resp.status_code}")
            return {}

    @staticmethod
    def generarTexto(objetivo, conversacion):
        return Gemini.generarRespuesta(objetivo, conversacion)
