"""
Módulo para extraer información de perfiles de LinkedIn usando Selenium
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from app.utils.config import get


class LinkedinScraper:
    
    def __init__(self):
        self.driver = None
        self.credentials = {
            "email": get("LINKEDIN_EMAIL"),
            "password": get("LINKEDIN_PASSWORD")
        }
    
    def setup_driver(self):
        """Configura el driver de Selenium"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--headless")  # Ejecutar en modo headless
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return True
        except Exception as e:
            print(f"Error configurando Selenium: {str(e)}")
            return False
    
    def hacer_login(self):
        """Hace login en LinkedIn"""
        try:
            self.driver.get("https://www.linkedin.com/login")
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            email_field = self.driver.find_element(By.ID, "username")
            email_field.clear()
            email_field.send_keys(self.credentials["email"])
            
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.credentials["password"])
            
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            try:
                WebDriverWait(self.driver, 30).until(
                    lambda d: "feed" in d.current_url or "in/" in d.current_url or "mynetwork" in d.current_url
                )
                return True
                
            except TimeoutException:
                if "challenge" in self.driver.page_source.lower():
                    raise Exception("LinkedIn requiere verificación (captcha). Ejecuta el script manualmente una vez.")
                return False
            
        except Exception as e:
            print(f"Error durante el login: {str(e)}")
            return False
    
    def extraer_info_personal(self):
        """Extrae información personal del perfil"""
        info_personal = {}
        
        try:
            name_element = self.driver.find_element(By.CSS_SELECTOR, "h1")
            info_personal["nombre"] = name_element.text.strip()
        except:
            pass
        
        try:
            title_selectors = [".text-body-medium", ".top-card-layout__headline"]
            for selector in title_selectors:
                try:
                    title_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    info_personal["titulo"] = title_element.text.strip()
                    break
                except:
                    continue
        except:
            pass
        
        try:
            location_selectors = [".text-body-small", ".top-card__subline-item"]
            for selector in location_selectors:
                try:
                    location_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    info_personal["ubicacion"] = location_element.text.strip()
                    break
                except:
                    continue
        except:
            pass
        
        try:
            acerca_section = self.driver.find_element(By.ID, "about")
            parrafos = acerca_section.find_elements(By.TAG_NAME, "p")
            for parrafo in parrafos:
                texto = parrafo.text.strip()
                if texto and len(texto) > 10:
                    info_personal["acerca_de"] = texto
                    break
        except:
            pass
        
        return info_personal
    
    def extraer_experiencia(self):
        """Extrae experiencia del perfil"""
        experiencias = []
        
        try:
            exp_section = self.driver.find_element(By.ID, "experience")
            self.driver.execute_script("arguments[0].scrollIntoView();", exp_section)
            time.sleep(2)
            
            exp_items = self.driver.find_elements(By.CSS_SELECTOR, "#experience ~ .artdeco-card li.artdeco-list__item")
            if not exp_items:
                exp_items = self.driver.find_elements(By.XPATH, "//section[descendant::div[@id='experience']]//li[contains(@class, 'artdeco-list__item')]")
            
            for item in exp_items:
                try:
                    texto_completo = item.text
                    if not texto_completo or len(texto_completo) < 10 or "Experiencia" in texto_completo:
                        continue
                    
                    experiencia = {}
                    lineas = [line.strip() for line in texto_completo.split('\n') if line.strip()]
                    
                    if len(lineas) > 0:
                        experiencia["empresa"] = lineas[0]
                    if len(lineas) > 1:
                        if any(p in lineas[1].lower() for p in ["año", "mes", "actualidad"]):
                            experiencia["fechas"] = lineas[1]
                        else:
                            experiencia["titulo"] = lineas[1]
                    
                    for linea in lineas:
                        if any(palabra in linea for palabra in ["año", "mes", "actualidad", "2024", "2023", "ago.", "sept."]):
                            if not experiencia.get("fechas"):
                                experiencia["fechas"] = linea
                            break
                    
                    for linea in lineas:
                        if any(palabra in linea for palabra in ["Argentina", "Buenos Aires", "Provincia", "Híbrido", "Remoto"]):
                            experiencia["ubicacion"] = linea
                            break
                    
                    descripcion = "\n".join([linea for linea in lineas if len(linea) > 50])
                    if descripcion:
                        experiencia["descripcion"] = descripcion
                    
                    if experiencia and (experiencia.get("empresa") or experiencia.get("titulo")):
                        experiencias.append(experiencia)
                
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"Error extrayendo experiencia: {str(e)}")
        
        return experiencias
    
    def extraer_educacion(self):
        """Extrae educación del perfil"""
        educaciones = []
        
        try:
            edu_section = self.driver.find_element(By.ID, "education")
            self.driver.execute_script("arguments[0].scrollIntoView();", edu_section)
            time.sleep(2)
            
            edu_items = self.driver.find_elements(By.XPATH, "//section[descendant::div[@id='education']]//li[contains(@class, 'artdeco-list__item')]")
            
            for item in edu_items:
                try:
                    texto_completo = item.text
                    if not texto_completo or len(texto_completo) < 10 or "Educación" in texto_completo:
                        continue
                    
                    educacion = {}
                    lineas = [line.strip() for line in texto_completo.split('\n') if line.strip()]
                    
                    if len(lineas) > 0:
                        educacion["institucion"] = lineas[0]
                    if len(lineas) > 1:
                        educacion["grado"] = lineas[1]
                    
                    for linea in lineas:
                        if any(palabra in linea for palabra in ["año", "mes", "actualidad", "2024", "2023"]):
                            educacion["fechas"] = linea
                            break
                    
                    if educacion and educacion.get("institucion"):
                        educaciones.append(educacion)
                
                except:
                    continue
            
        except:
            pass
        
        return educaciones
    
    def extraer_certificaciones(self):
        """Extrae certificaciones del perfil"""
        licencias = []
        
        try:
            lic_section = self.driver.find_element(By.ID, "licenses_and_certifications")
            self.driver.execute_script("arguments[0].scrollIntoView();", lic_section)
            time.sleep(2)
            
            lic_items = self.driver.find_elements(By.XPATH, "//section[descendant::div[@id='licenses_and_certifications']]//li[contains(@class, 'artdeco-list__item')]")
            
            for item in lic_items:
                try:
                    texto_completo = item.text
                    if not texto_completo or len(texto_completo) < 5 or "licencias" in texto_completo.lower():
                        continue
                    
                    licencia = {}
                    lineas = [line.strip() for line in texto_completo.split('\n') if line.strip()]
                    
                    if len(lineas) > 0:
                        licencia["nombre"] = lineas[0]
                    if len(lineas) > 1:
                        licencia["organizacion"] = lineas[1]
                    
                    for linea in lineas:
                        if any(palabra in linea for palabra in ["2024", "2023", "mar.", "abr.", "jul."]):
                            licencia["fecha_emision"] = linea
                            break
                    
                    if licencia and licencia.get("nombre"):
                        licencias.append(licencia)
                
                except:
                    continue
            
        except:
            pass
        
        return licencias
    
    def extraer_info_completa(self, url_perfil):
        """
        Extrae toda la información de un perfil de LinkedIn
        """
        try:
            # Setup del driver
            if not self.setup_driver():
                return None
            
            # Login
            if not self.hacer_login():
                print("No se pudo hacer login en LinkedIn")
                return None
            
            # Ir al perfil
            self.driver.get(url_perfil)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(3)  # Dar tiempo para que cargue
            
            # Extraer información
            info = {
                "informacion_personal": self.extraer_info_personal(),
                "experiencia": self.extraer_experiencia(),
                "educacion": self.extraer_educacion(),
                "licencias_certificaciones": self.extraer_certificaciones()
            }
            
            return info
            
        except Exception as e:
            print(f"Error extrayendo info completa: {str(e)}")
            return None
        finally:
            if self.driver:
                self.driver.quit()

