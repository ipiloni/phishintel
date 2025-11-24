import subprocess
import time
import requests
import os
from flask import jsonify
from app.backend.models.error import responseError
from app.utils.logger import log

try:
    from pyngrok import ngrok
    PYNGROK_AVAILABLE = True
except ImportError:
    PYNGROK_AVAILABLE = False


class NgrokController:
    
    @staticmethod
    def crear_tunel_temporal(puerto=8080):
        """
        Crea un túnel temporal de ngrok para el puerto especificado.
        
        Args:
            puerto (int): Puerto local al que hacer túnel (por defecto 8080)
            
        Returns:
            tuple: (response, status_code) con la URL del túnel o error
        """
        log.info(f"Creando túnel temporal de ngrok para puerto {puerto}")
        
        try:
            # Obtener el token de ngrok desde las variables de entorno
            token = os.environ.get("NGROK_TOKEN")
            if not token:
                log.error("Token de ngrok no configurado")
                return responseError("TOKEN_NO_CONFIGURADO", "Token de ngrok no configurado", 500)
            
            # Intentar usar pyngrok primero (más fácil)
            if PYNGROK_AVAILABLE:
                log.info("Usando pyngrok para crear el túnel")
                try:
                    # Configurar el token
                    ngrok.set_auth_token(token)
                    
                    # Crear el túnel
                    tunnel = ngrok.connect(puerto, "http")
                    public_url = tunnel.public_url
                    
                    log.info(f"Túnel ngrok creado exitosamente con pyngrok: {public_url}")
                    return jsonify({
                        "mensaje": "Túnel ngrok creado exitosamente",
                        "url_publica": public_url,
                        "puerto_local": puerto,
                        "metodo": "pyngrok"
                    }), 201
                    
                except Exception as e:
                    log.warn(f"Error con pyngrok, intentando con subprocess: {str(e)}")
                    # Si pyngrok falla, continuar con subprocess
            
            # Fallback: usar subprocess (ngrok CLI)
            log.info("Usando subprocess para crear el túnel")
            
            # Configurar el token de ngrok
            subprocess.run(['ngrok', 'config', 'add-authtoken', token], 
                         capture_output=True, text=True, check=True)
            
            # Crear el túnel
            log.info(f"Iniciando túnel ngrok para puerto {puerto}")
            process = subprocess.Popen(
                ['ngrok', 'http', str(puerto), '--log=stdout'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Esperar un momento para que ngrok se inicie
            time.sleep(3)
            
            # Obtener la URL del túnel desde la API local de ngrok
            try:
                response = requests.get('http://localhost:4040/api/tunnels', timeout=10)
                if response.status_code == 200:
                    tunnels_data = response.json()
                    tunnels = tunnels_data.get('tunnels', [])
                    
                    if tunnels:
                        # Buscar el túnel HTTP (no HTTPS)
                        for tunnel in tunnels:
                            if tunnel.get('proto') == 'http' and tunnel.get('config', {}).get('addr') == f'localhost:{puerto}':
                                public_url = tunnel.get('public_url')
                                if public_url:
                                    log.info(f"Túnel ngrok creado exitosamente: {public_url}")
                                    return jsonify({
                                        "mensaje": "Túnel ngrok creado exitosamente",
                                        "url_publica": public_url,
                                        "puerto_local": puerto,
                                        "proceso_id": process.pid,
                                        "metodo": "subprocess"
                                    }), 201
                    
                    # Si no encontramos el túnel específico, usar el primero disponible
                    if tunnels:
                        public_url = tunnels[0].get('public_url')
                        if public_url:
                            log.info(f"Túnel ngrok creado exitosamente (primer túnel disponible): {public_url}")
                            return jsonify({
                                "mensaje": "Túnel ngrok creado exitosamente",
                                "url_publica": public_url,
                                "puerto_local": puerto,
                                "proceso_id": process.pid,
                                "metodo": "subprocess"
                            }), 201
                
                log.error("No se pudo obtener la URL del túnel desde la API de ngrok")
                return responseError("ERROR_API_NGROK", "No se pudo obtener la URL del túnel", 500)
                
            except requests.exceptions.RequestException as e:
                log.error(f"Error al consultar la API de ngrok: {str(e)}")
                return responseError("ERROR_API_NGROK", f"Error al consultar la API de ngrok: {str(e)}", 500)
                
        except subprocess.CalledProcessError as e:
            log.error(f"Error al configurar ngrok: {str(e)}")
            return responseError("ERROR_NGROK_CONFIG", f"Error al configurar ngrok: {str(e)}", 500)
        except FileNotFoundError:
            log.error("ngrok no está instalado o no está en el PATH")
            return responseError("NGROK_NO_INSTALADO", "ngrok no está instalado o no está en el PATH. Instala ngrok o ejecuta: pip install pyngrok", 404)
        except Exception as e:
            log.error(f"Error inesperado al crear túnel ngrok: {str(e)}")
            return responseError("ERROR_NGROK", f"Error inesperado: {str(e)}", 500)
    
    @staticmethod
    def obtener_url_tunel_actual():
        """
        Obtiene la URL del túnel ngrok actualmente activo.
        
        Returns:
            tuple: (response, status_code) con la URL del túnel o error
        """
        log.info("Obteniendo URL del túnel ngrok actual")
        
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=10)
            if response.status_code == 200:
                tunnels_data = response.json()
                tunnels = tunnels_data.get('tunnels', [])
                
                if tunnels:
                    # Buscar el túnel HTTP
                    for tunnel in tunnels:
                        if tunnel.get('proto') == 'http':
                            public_url = tunnel.get('public_url')
                            if public_url:
                                log.info(f"Túnel ngrok encontrado: {public_url}")
                                return jsonify({
                                    "mensaje": "Túnel ngrok encontrado",
                                    "url_publica": public_url,
                                    "estado": tunnel.get('state', 'unknown')
                                }), 200
                    
                    # Si no hay túnel HTTP, usar el primero disponible
                    public_url = tunnels[0].get('public_url')
                    if public_url:
                        log.info(f"Túnel ngrok encontrado (primer túnel disponible): {public_url}")
                        return jsonify({
                            "mensaje": "Túnel ngrok encontrado",
                            "url_publica": public_url,
                            "estado": tunnels[0].get('state', 'unknown')
                        }), 200
                
                log.warn("No hay túneles ngrok activos")
                return responseError("NO_TUNELES_ACTIVOS", "No hay túneles ngrok activos", 404)
                
            else:
                log.error(f"Error al consultar la API de ngrok: {response.status_code}")
                return responseError("ERROR_API_NGROK", f"Error al consultar la API de ngrok: {response.status_code}", 500)
                
        except requests.exceptions.RequestException as e:
            log.error(f"Error al consultar la API de ngrok: {str(e)}")
            return responseError("ERROR_API_NGROK", f"Error al consultar la API de ngrok: {str(e)}", 500)
        except Exception as e:
            log.error(f"Error inesperado al obtener túnel ngrok: {str(e)}")
            return responseError("ERROR_NGROK", f"Error inesperado: {str(e)}", 500)
    
    @staticmethod
    def cerrar_tuneles():
        """
        Cierra todos los túneles ngrok activos.
        
        Returns:
            tuple: (response, status_code)
        """
        log.info("Cerrando túneles ngrok activos")
        
        try:
            # Obtener información de túneles activos
            response = requests.get('http://localhost:4040/api/tunnels', timeout=10)
            if response.status_code == 200:
                tunnels_data = response.json()
                tunnels = tunnels_data.get('tunnels', [])
                
                if not tunnels:
                    log.info("No hay túneles ngrok activos para cerrar")
                    return jsonify({
                        "mensaje": "No hay túneles ngrok activos para cerrar"
                    }), 200
                
                # Cerrar cada túnel
                for tunnel in tunnels:
                    tunnel_name = tunnel.get('name', 'unknown')
                    try:
                        delete_response = requests.delete(f'http://localhost:4040/api/tunnels/{tunnel_name}', timeout=10)
                        if delete_response.status_code == 204:
                            log.info(f"Túnel {tunnel_name} cerrado exitosamente")
                        else:
                            log.warn(f"Error al cerrar túnel {tunnel_name}: {delete_response.status_code}")
                    except requests.exceptions.RequestException as e:
                        log.warn(f"Error al cerrar túnel {tunnel_name}: {str(e)}")
                
                log.info("Proceso de cierre de túneles completado")
                return jsonify({
                    "mensaje": "Túneles ngrok cerrados exitosamente",
                    "tuneles_cerrados": len(tunnels)
                }), 200
                
            else:
                log.error(f"Error al consultar la API de ngrok: {response.status_code}")
                return responseError("ERROR_API_NGROK", f"Error al consultar la API de ngrok: {response.status_code}", 500)
                
        except requests.exceptions.RequestException as e:
            log.error(f"Error al consultar la API de ngrok: {str(e)}")
            return responseError("ERROR_API_NGROK", f"Error al consultar la API de ngrok: {str(e)}", 500)
        except Exception as e:
            log.error(f"Error inesperado al cerrar túneles ngrok: {str(e)}")
            return responseError("ERROR_NGROK", f"Error inesperado: {str(e)}", 500)
