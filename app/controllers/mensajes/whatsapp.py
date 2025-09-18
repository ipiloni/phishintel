import shutil
import tempfile
import requests
import time
import os
import re

from flask import jsonify
from twilio.rest import Client
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException

from app.backend.models.error import responseError
from app.utils.config import get
from app.utils.logger import log
from app.controllers.ngrokController import NgrokController


class WhatsAppController:
    
    @staticmethod
    def enviarMensajeTwilio(data):
        """
        Envía un mensaje de WhatsApp usando Twilio API.
        
        Args:
            data (dict): Diccionario con los siguientes campos:
                - mensaje (str): Mensaje a enviar
                - destinatario (str): Número de teléfono del destinatario
                
        Returns:
            tuple: (response, status_code)
        """
        log.info("Se recibió una solicitud para enviar mensaje via WhatsApp (Twilio)")

        if not data or "mensaje" not in data or "destinatario" not in data:
            log.warn("Faltan campos obligatorios")
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios (mensaje o destinatario)", 400)

        try:
            account_sid = get("TWILIO_ACCOUNT_SID_IGNA")
            auth_token = get("TWILIO_AUTH_TOKEN_IGNA")
            
            if not account_sid or not auth_token:
                log.error("Credenciales de Twilio no configuradas")
                return responseError("CREDENCIALES_NO_CONFIGURADAS", "Credenciales de Twilio no configuradas", 500)

            client = Client(account_sid, auth_token)

            message = client.messages.create(
                body=data["mensaje"],
                from_='whatsapp:+14155238886',
                to='whatsapp:' + data["destinatario"]
            )

            log.info("WhatsApp enviado con SID: " + message.sid)

            return jsonify({"mensaje": f"WhatsApp enviado con SID: {message.sid}"}), 201
        except Exception as e:
            log.error("Hubo un error al enviar mensaje por WhatsApp: " + str(e))
            return responseError("ERROR_API", "Hubo un error al enviar mensaje por WhatsApp: " + str(e), 500)

    @staticmethod
    def enviarMensajeSelenium(data):
        """
        Envía un mensaje de WhatsApp usando Selenium WebDriver.
        Requiere que el usuario esté previamente logueado en WhatsApp Web en Chrome.

        Args:
            data (dict): Diccionario con los siguientes campos:
                - mensaje (str): Mensaje a enviar
                - destinatario (str): Número de teléfono o nombre del contacto

        Returns:
            tuple: (response, status_code)
        """
        log.info("Se recibió una solicitud para enviar mensaje via WhatsApp con Selenium")

        # Validar campos obligatorios
        if not data or "destinatario" not in data or "mensaje" not in data:
            log.warn("Faltan campos obligatorios para envío con Selenium")
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios (destinatario o mensaje)", 400)

        destinatario = data["destinatario"]
        mensaje = data["mensaje"]

        driver = None
        temp_dir = None
        try:
            # Configurar Chrome con opciones para mantener la sesión
            chrome_options = Options()

            # Crear un directorio temporal único
            temp_dir = tempfile.mkdtemp(prefix="chrome_selenium_")
            log.info(f"Usando directorio temporal: {temp_dir}")

            # Obtener el path correcto para el directorio de datos de usuario de Chrome
            user_data_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "User Data")
            profile_path = os.path.join(user_data_dir, "Profile 14")

            # Verificar que el directorio del perfil existe
            if not os.path.exists(profile_path):
                log.error(f"El perfil Profile 14 no existe en: {profile_path}")
                return responseError("PERFIL_NO_EXISTE", f"El perfil Profile 14 no existe en: {profile_path}", 404)

            # Copiar el perfil al directorio temporal
            temp_profile_path = os.path.join(temp_dir, "Profile 14")
            try:
                shutil.copytree(profile_path, temp_profile_path)
                log.info(f"Perfil copiado a directorio temporal: {temp_profile_path}")
            except Exception as e:
                log.error(f"Error al copiar el perfil: {str(e)}")
                return responseError("ERROR_COPIA_PERFIL", f"Error al copiar el perfil: {str(e)}", 500)

            chrome_options.add_argument(f"--user-data-dir={temp_dir}")
            chrome_options.add_argument("--profile-directory=Profile 14")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("detach", True)

            log.info(f"Usando directorio de datos de Chrome: {user_data_dir}")
            log.info(f"Perfil Profile 14 encontrado en: {profile_path}")

            # Verificar que ChromeDriver existe
            chromedriver_path = r"D:\chromedriver-win64\chromedriver-win64\chromedriver.exe"
            if not os.path.exists(chromedriver_path):
                log.error(f"ChromeDriver no encontrado en: {chromedriver_path}")
                return responseError("CHROMEDRIVER_NO_ENCONTRADO",
                                     f"ChromeDriver no encontrado en: {chromedriver_path}", 404)

            log.info(f"ChromeDriver encontrado en: {chromedriver_path}")

            # Agregar la ruta del ChromeDriver al PATH
            chromedriver_dir = os.path.dirname(chromedriver_path)
            if chromedriver_dir not in os.environ.get('PATH', ''):
                os.environ['PATH'] = chromedriver_dir + os.path.sep + os.environ.get('PATH', '')

            # Inicializar el driver
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.get("https://web.whatsapp.com")

            # Esperar a que WhatsApp Web cargue
            wait = WebDriverWait(driver, 30, ignored_exceptions=[StaleElementReferenceException])

            # Esperar a que aparezca el input de búsqueda
            search_box = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
            log.info("WhatsApp Web cargado correctamente")

            # Buscar contacto
            actions = ActionChains(driver)
            actions.click(search_box).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(
                destinatario).perform()
            log.info(f"Buscando contacto: '{destinatario}'")

            # Esperar a que aparezcan los resultados de búsqueda
            time.sleep(3)

            # Seleccionar contacto con reintentos para stale elements
            contact_selectors = [
                '//div[@data-testid="cell-frame-container"]',
                '//div[@data-testid="chat-list"]//div[@data-testid="cell-frame-container"]',
                '//div[contains(@class, "_ak8l")]//div[@data-testid="cell-frame-container"]',
                '//div[@role="listitem"]//div[@data-testid="cell-frame-container"]'
            ]

            first_chat = None
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    for selector in contact_selectors:
                        try:
                            first_chat = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                            actions = ActionChains(driver)
                            actions.move_to_element(first_chat).pause(0.5).click().perform()
                            log.info(f"Contacto '{destinatario}' seleccionado correctamente con selector: {selector}")
                            break
                        except TimeoutException:
                            continue
                    if first_chat:
                        break
                except StaleElementReferenceException:
                    if attempt == max_retries - 1:
                        log.error(f"No se pudo seleccionar el contacto '{destinatario}' tras {max_retries} intentos")
                        return responseError("CONTACTO_NO_ENCONTRADO", f"No se encontró el contacto '{destinatario}'",
                                             404)
                    time.sleep(1)
                    log.warn(f"Reintentando selección de contacto (intento {attempt + 1})")
                    continue

            if not first_chat:
                log.error(f"No se encontró el contacto '{destinatario}' con ningún selector")
                return responseError("CONTACTO_NO_ENCONTRADO",
                                     f"No se encontró el contacto '{destinatario}'. Verifica que el contacto existe en WhatsApp.",
                                     404)

            # Esperar a que se abra el chat
            time.sleep(3)

            # Escribir mensaje con reintentos para stale elements
            message_selectors = [
                '//div[@contenteditable="true"][@data-tab="10"]',
                '//div[@contenteditable="true"][@data-tab="9"]',
                '//div[@contenteditable="true"][@title="Escribe un mensaje"]',
                '//div[@contenteditable="true"][contains(@class, "selectable-text")]'
            ]

            message_box = None
            for attempt in range(max_retries):
                try:
                    for selector in message_selectors:
                        try:
                            message_box = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                            message_box.click()
                            time.sleep(0.5)
                            message_box.clear()
                            time.sleep(0.5)

                            # Escribir carácter por carácter para simular escritura humana
                            for char in mensaje:
                                message_box.send_keys(char)
                                time.sleep(0.05)

                            log.info(f"Mensaje escrito: '{mensaje}'")
                            break
                        except TimeoutException:
                            continue
                    if message_box:
                        break
                except StaleElementReferenceException:
                    if attempt == max_retries - 1:
                        log.error("No se pudo escribir el mensaje tras múltiples intentos")
                        return responseError("CAMPO_MENSAJE_NO_ENCONTRADO",
                                             "No se pudo encontrar o usar el campo de mensaje", 500)
                    time.sleep(1)
                    log.warn(f"Reintentando escritura de mensaje (intento {attempt + 1})")
                    continue

            if not message_box:
                log.error("No se pudo encontrar el campo de mensaje")
                return responseError("CAMPO_MENSAJE_NO_ENCONTRADO",
                                     "No se pudo encontrar el campo de mensaje en WhatsApp Web", 500)

            # Esperar un momento antes de enviar
            time.sleep(2)

            # Enviar mensaje con reintentos para stale elements
            send_selectors = [
                '//button[@data-testid="send"]',
                '//button[@data-testid="send-button"]',
                '//span[@data-testid="send"]',
                '//button[contains(@class, "send-button")]'
            ]

            send_button = None
            for attempt in range(max_retries):
                try:
                    for selector in send_selectors:
                        try:
                            send_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                            actions = ActionChains(driver)
                            actions.move_to_element(send_button).pause(0.5).click().perform()
                            log.info("Mensaje enviado correctamente")
                            break
                        except TimeoutException:
                            continue
                    if send_button:
                        break
                except StaleElementReferenceException:
                    if attempt == max_retries - 1:
                        log.error("No se pudo enviar el mensaje tras múltiples intentos")
                        return responseError("BOTON_ENVIAR_NO_ENCONTRADO",
                                             "No se pudo encontrar o usar el botón de enviar", 500)
                    time.sleep(1)
                    log.warn(f"Reintentando envío de mensaje (intento {attempt + 1})")
                    continue

            if not send_button:
                log.error("No se pudo encontrar el botón de enviar")
                return responseError("BOTON_ENVIAR_NO_ENCONTRADO",
                                     "No se pudo encontrar el botón de enviar en WhatsApp Web", 500)

            # Esperar un momento para asegurar que el mensaje se envíe
            time.sleep(3)

            return jsonify({
                "mensaje": f"Mensaje enviado correctamente a '{destinatario}'",
                "destinatario": destinatario,
                "contenido": mensaje
            }), 201

        except TimeoutException as e:
            log.error(f"Timeout al cargar WhatsApp Web: {str(e)}")
            return responseError("TIMEOUT_ERROR",
                                 "Timeout al cargar WhatsApp Web. Asegúrate de estar logueado en Profile 14.", 408)
        except NoSuchElementException as e:
            log.error(f"Elemento no encontrado en WhatsApp Web: {str(e)}")
            return responseError("ELEMENTO_NO_ENCONTRADO", "No se pudo encontrar un elemento necesario en WhatsApp Web",
                                 500)
        except Exception as e:
            error_msg = str(e)
            if "cannot create default profile directory" in error_msg:
                log.error(f"Error de perfil de Chrome: {error_msg}")
                return responseError("PERFIL_CHROME_ERROR",
                                     "Error al acceder al perfil de Chrome. Asegúrate de que Profile 14 existe y no está en uso.",
                                     500)
            elif "session not created" in error_msg:
                log.error(f"Error de sesión de Chrome: {error_msg}")
                return responseError("SESION_CHROME_ERROR",
                                     "Error al crear sesión de Chrome. Verifica que ChromeDriver esté instalado y sea compatible.",
                                     500)
            elif "Profile 14" in error_msg and "not exist" in error_msg:
                log.error(f"Perfil no encontrado: {error_msg}")
                return responseError("PERFIL_NO_EXISTE",
                                     "El perfil Profile 14 no existe. Verifica que el perfil esté creado correctamente.",
                                     404)
            elif "ChromeDriver" in error_msg and "not found" in error_msg:
                log.error(f"ChromeDriver no encontrado: {error_msg}")
                return responseError("CHROMEDRIVER_NO_ENCONTRADO",
                                     "ChromeDriver no encontrado. Verifica la ruta del ejecutable.", 404)
            elif "user data directory is already in use" in error_msg:
                log.error(f"Directorio de datos de usuario en uso: {error_msg}")
                return responseError("DIRECTORIO_EN_USO",
                                     "El directorio de datos de Chrome está en uso. Cierra Chrome y vuelve a intentar.",
                                     409)
            elif "stale element reference" in error_msg:
                log.error(f"Elemento obsoleto: {error_msg}")
                return responseError("ELEMENTO_OBSOLETO",
                                     "El elemento de la página cambió durante la operación. Intenta nuevamente.", 500)
            else:
                log.error(f"Error inesperado al enviar mensaje con Selenium: {error_msg}")
                return responseError("ERROR_SELENIUM", f"Error inesperado: {error_msg}", 500)
        finally:
            # Cerrar el navegador
            if driver:
                try:
                    driver.quit()
                    log.info("Navegador cerrado correctamente")
                except Exception as e:
                    log.warn(f"Error al cerrar el navegador: {str(e)}")

            # Limpiar el directorio temporal
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    log.info(f"Directorio temporal eliminado: {temp_dir}")
                except Exception as e:
                    log.warn(f"Error al eliminar directorio temporal: {str(e)}")

    @staticmethod
    def enviarMensajeWhapi(data):
        """
        Envía un mensaje de WhatsApp usando whapi.cloud API.

        Args:
            data (dict): Diccionario con los siguientes campos:
                - mensaje (str): Mensaje a enviar
                - destinatario (str, opcional): Número de teléfono del destinatario.
                  Si no se proporciona, se usa el número por defecto +54 9 11 4163-5935

        Returns:
            tuple: (response, status_code)
        """
        log.info("Se recibió una solicitud para enviar mensaje via WhatsApp con whapi.cloud")

        # Validar campos obligatorios
        if not data or "mensaje" not in data:
            log.warn("Falta el campo obligatorio 'mensaje'")
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'mensaje'", 400)

        mensaje = data["mensaje"]
        #destinatario = data.get("destinatario", "+54 9 11 4163-5935")  # Número por defecto
        destinatario = "+54 9 11 4163-5935"

        # Formatear el número: solo dígitos, formato internacional sin +
        destinatario_limpio = ''.join(c for c in destinatario if c.isdigit())
        if destinatario_limpio.startswith('0'):
            destinatario_limpio = destinatario_limpio[1:]  # Remover 0 inicial si es local
        if not destinatario_limpio.startswith('54'):
            # Asumir que es local argentino y agregar 54 9
            if len(destinatario_limpio) == 10:  # Ej: 91141635935
                destinatario_formateado = '549' + destinatario_limpio
            else:
                return responseError("NUMERO_INVALIDO", "Formato de número no reconocido", 400)
        else:
            destinatario_formateado = destinatario_limpio

        # Validar longitud aproximada (para Argentina: 13 dígitos)
        if len(destinatario_formateado) != 13 or not destinatario_formateado.startswith('549'):
            return responseError("NUMERO_INVALIDO", f"Número inválido: {destinatario_formateado}", 400)

        try:
            # Obtener el token desde las variables de entorno
            token = get("WHAPI_CLOUD_TOKEN")
            if not token:
                log.error("Token de whapi.cloud no configurado")
                return responseError("TOKEN_NO_CONFIGURADO", "Token de whapi.cloud no configurado", 500)

            # URL de la API de whapi.cloud
            url = "https://gate.whapi.cloud/messages/text"

            # Headers para la petición
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            # Datos del mensaje
            payload = {
                "to": destinatario_formateado,
                "body": mensaje
            }

            log.info(f"Enviando mensaje a {destinatario} (formateado: {destinatario_formateado}): {mensaje}")

            # Realizar la petición POST
            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                response_data = response.json()
                log.info(f"Mensaje enviado correctamente. ID: {response_data.get('id', 'N/A')}")
                return jsonify({
                    "mensaje": "Mensaje enviado correctamente via whapi.cloud",
                    "destinatario": destinatario,
                    "destinatario_formateado": destinatario_formateado,
                    "contenido": mensaje,
                    "id": response_data.get('id', 'N/A')
                }), 201
            else:
                error_msg = f"Error en whapi.cloud API: {response.status_code} - {response.text}"
                log.error(error_msg)
                return responseError("ERROR_API_WHAPI", error_msg, response.status_code)

        except requests.exceptions.Timeout:
            log.error("Timeout al enviar mensaje via whapi.cloud")
            return responseError("TIMEOUT_ERROR", "Timeout al enviar mensaje via whapi.cloud", 408)
        except requests.exceptions.ConnectionError:
            log.error("Error de conexión con whapi.cloud")
            return responseError("CONNECTION_ERROR", "Error de conexión con whapi.cloud", 503)
        except Exception as e:
            error_msg = f"Error inesperado al enviar mensaje con whapi.cloud: {str(e)}"
            log.error(error_msg)
            return responseError("ERROR_WHAPI", error_msg, 500)

    @staticmethod
    def enviarMensajeWhapiGrupo(data):
        """
        Envía un mensaje de WhatsApp a un grupo usando whapi.cloud API.

        Args:
            data (dict): Diccionario con los siguientes campos:
                - mensaje (str): Mensaje a enviar
                - grupo_id (str, opcional): ID del grupo de WhatsApp.
                  Si no se proporciona, se usa el grupo por defecto "Proyecto Grupo 8 🤝🏻✨🎉🙌🏻"

        Returns:
            tuple: (response, status_code)
        """
        log.info("Se recibió una solicitud para enviar mensaje a grupo de WhatsApp con whapi.cloud")

        # Validar campos obligatorios
        if not data or "mensaje" not in data:
            log.warn("Falta el campo obligatorio 'mensaje'")
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'mensaje'", 400)

        mensaje = data["mensaje"]
        grupo_id = data.get("grupo_id", "120363416003158863@g.us")  # Grupo por defecto

        try:
            # Obtener el token desde las variables de entorno
            token = get("WHAPI_CLOUD_TOKEN")
            if not token:
                log.error("Token de whapi.cloud no configurado")
                return responseError("TOKEN_NO_CONFIGURADO", "Token de whapi.cloud no configurado", 500)

            # URL de la API de whapi.cloud
            url = "https://gate.whapi.cloud/messages/text"

            # Headers para la petición
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            # Datos del mensaje
            payload = {
                "to": grupo_id,
                "body": mensaje
            }

            log.info(f"Enviando mensaje al grupo '{grupo_id}': {mensaje}")

            # Realizar la petición POST
            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                response_data = response.json()
                log.info(f"Mensaje enviado correctamente al grupo. ID: {response_data.get('id', 'N/A')}")
                return jsonify({
                    "mensaje": "Mensaje enviado correctamente al grupo via whapi.cloud",
                    "grupo_id": grupo_id,
                    "contenido": mensaje,
                    "id": response_data.get('id', 'N/A')
                }), 201
            else:
                error_msg = f"Error en whapi.cloud API: {response.status_code} - {response.text}"
                log.error(error_msg)
                return responseError("ERROR_API_WHAPI", error_msg, response.status_code)

        except requests.exceptions.Timeout:
            log.error("Timeout al enviar mensaje al grupo via whapi.cloud")
            return responseError("TIMEOUT_ERROR", "Timeout al enviar mensaje al grupo via whapi.cloud", 408)
        except requests.exceptions.ConnectionError:
            log.error("Error de conexión con whapi.cloud")
            return responseError("CONNECTION_ERROR", "Error de conexión con whapi.cloud", 503)
        except Exception as e:
            error_msg = f"Error inesperado al enviar mensaje al grupo con whapi.cloud: {str(e)}"
            log.error(error_msg)
            return responseError("ERROR_WHAPI", error_msg, 500)

    @staticmethod
    def enviarMensajeWhapiLinkPreview(data):
        """
        Envía un mensaje de WhatsApp con preview de enlace personalizado usando whapi.cloud API.
        Usa el endpoint /messages/link-preview para crear enlaces clickeables con preview.
        Crea un túnel ngrok temporal para el enlace.
        
        IMPORTANTE: El mensaje DEBE contener el enlace en el texto para que funcione el preview.

        Args:
            data (dict): Diccionario con los siguientes campos:
                - mensaje (str): Mensaje a enviar (DEBE contener el enlace en el texto)
                - destinatario (str, opcional): Número de teléfono del destinatario.
                  Si no se proporciona, se usa el número por defecto +54 9 11 4163-5935
                - titulo (str, opcional): Título del enlace. Por defecto "Enlace"
                - media (str, opcional): URL de la imagen para el preview. Por defecto None
                - idUsuario (int, opcional): ID del usuario para el enlace
                - idEvento (int, opcional): ID del evento para el enlace

        Returns:
            tuple: (response, status_code)
        """
        log.info("Se recibió una solicitud para enviar mensaje con link preview via WhatsApp con whapi.cloud")

        # Validar campos obligatorios
        if not data or "mensaje" not in data:
            log.warn("Falta el campo obligatorio 'mensaje'")
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'mensaje'", 400)

        mensaje = data["mensaje"]
        destinatario = data.get("destinatario", "+54 9 11 4163-5935")
        titulo = data.get("titulo", "Enlace")
        media = data.get("media")
        id_usuario = data.get("idUsuario")
        id_evento = data.get("idEvento")

        # Crear túnel ngrok temporal si se proporcionan los IDs
        url_enlace = None
        if id_usuario and id_evento:
            log.info("Creando túnel ngrok temporal para el enlace")
            ngrok_result = NgrokController.crear_tunel_temporal(8080)
            
            if isinstance(ngrok_result, tuple) and len(ngrok_result) == 2:
                response, status_code = ngrok_result
                if status_code == 201:
                    # Extraer la URL del túnel de la respuesta
                    if hasattr(response, 'get_json'):
                        response_data = response.get_json()
                        url_publica = response_data.get('url_publica')
                        if url_publica:
                            # Construir el enlace completo con los parámetros
                            url_enlace = f"{url_publica}/caiste?idUsuario={id_usuario}&idEvento={id_evento}"
                            log.info(f"Enlace ngrok creado: {url_enlace}")
                        else:
                            log.error("No se pudo obtener la URL pública del túnel ngrok")
                            return responseError("ERROR_NGROK_URL", "No se pudo obtener la URL pública del túnel ngrok", 500)
                    else:
                        log.error("Respuesta de ngrok no válida")
                        return responseError("ERROR_NGROK_RESPONSE", "Respuesta de ngrok no válida", 500)
                else:
                    log.error(f"Error al crear túnel ngrok: {status_code}")
                    return ngrok_result
            else:
                log.error("Error inesperado al crear túnel ngrok")
                return responseError("ERROR_NGROK", "Error inesperado al crear túnel ngrok", 500)
        else:
            # Si no se proporcionan IDs, usar el enlace original del mensaje
            if "http://" in mensaje or "https://" in mensaje:
                # Extraer el enlace del mensaje
                import re
                url_match = re.search(r'https?://[^\s]+', mensaje)
                if url_match:
                    url_enlace = url_match.group()
                else:
                    log.warn("No se pudo extraer enlace del mensaje")
                    return responseError("ENLACE_NO_EXTRAIBLE", "No se pudo extraer enlace del mensaje", 400)
            else:
                log.warn("El mensaje debe contener un enlace para usar link preview")
                return responseError("ENLACE_REQUERIDO", "El mensaje debe contener un enlace (http:// o https://) para usar link preview", 400)

        # Reemplazar el enlace en el mensaje con el enlace ngrok si existe
        if url_enlace:
            # Reemplazar cualquier enlace en el mensaje con el enlace ngrok
            import re
            mensaje_con_ngrok = re.sub(r'https?://[^\s]+', url_enlace, mensaje)
            log.info(f"Mensaje actualizado con enlace ngrok: {mensaje_con_ngrok}")
        else:
            mensaje_con_ngrok = mensaje

        # Formatear el número: solo dígitos, formato internacional sin +
        destinatario_limpio = ''.join(c for c in destinatario if c.isdigit())
        if destinatario_limpio.startswith('0'):
            destinatario_limpio = destinatario_limpio[1:]  # Remover 0 inicial si es local
        if not destinatario_limpio.startswith('54'):
            # Asumir que es local argentino y agregar 54 9
            if len(destinatario_limpio) == 10:  # Ej: 91141635935
                destinatario_formateado = '549' + destinatario_limpio
            else:
                return responseError("NUMERO_INVALIDO", "Formato de número no reconocido", 400)
        else:
            destinatario_formateado = destinatario_limpio

        # Validar longitud aproximada (para Argentina: 13 dígitos)
        if len(destinatario_formateado) != 13 or not destinatario_formateado.startswith('549'):
            return responseError("NUMERO_INVALIDO", f"Número inválido: {destinatario_formateado}", 400)

        try:
            # Obtener el token desde las variables de entorno
            token = get("WHAPI_CLOUD_TOKEN")
            if not token:
                log.error("Token de whapi.cloud no configurado")
                return responseError("TOKEN_NO_CONFIGURADO", "Token de whapi.cloud no configurado", 500)

            # URL de la API de whapi.cloud para link preview
            url = "https://gate.whapi.cloud/messages/link_preview"

            # Headers para la petición
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            # Datos del mensaje con link preview - parámetros requeridos
            payload = {
                "to": destinatario_formateado,
                "body": mensaje_con_ngrok,
                "title": titulo
            }

            log.info(f"Enviando mensaje con link preview a {destinatario} (formateado: {destinatario_formateado})")
            log.info(f"Payload completo: {payload}")
            log.info(f"URL: {url}")
            log.info(f"Headers: {headers}")

            # Realizar la petición POST
            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                response_data = response.json()
                log.info(f"Mensaje con link preview enviado correctamente. ID: {response_data.get('id', 'N/A')}")
                return jsonify({
                    "mensaje": "Mensaje con link preview enviado correctamente via whapi.cloud",
                    "destinatario": destinatario,
                    "destinatario_formateado": destinatario_formateado,
                    "contenido": mensaje_con_ngrok,
                    "titulo": titulo,
                    "media": media,
                    "url_ngrok": url_enlace,
                    "id": response_data.get('id', 'N/A')
                }), 201
            else:
                error_msg = f"Error en whapi.cloud API: {response.status_code} - {response.text}"
                log.error(error_msg)
                return responseError("ERROR_API_WHAPI", error_msg, response.status_code)

        except requests.exceptions.Timeout:
            log.error("Timeout al enviar mensaje con link preview via whapi.cloud")
            return responseError("TIMEOUT_ERROR", "Timeout al enviar mensaje con link preview via whapi.cloud", 408)
        except requests.exceptions.ConnectionError:
            log.error("Error de conexión con whapi.cloud")
            return responseError("CONNECTION_ERROR", "Error de conexión con whapi.cloud", 503)
        except Exception as e:
            error_msg = f"Error inesperado al enviar mensaje con link preview con whapi.cloud: {str(e)}"
            log.error(error_msg)
            return responseError("ERROR_WHAPI", error_msg, 500)
