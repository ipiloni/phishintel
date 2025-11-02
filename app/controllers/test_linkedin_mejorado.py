#!/usr/bin/env python3
"""
Script mejorado para extraer información completa de LinkedIn
Basado en la estructura HTML real de LinkedIn
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

import time
import json

def setup_selenium_driver():
    """
    Configura el driver de Selenium
    """
    print("🔧 Configurando Selenium...")
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Comentado para que veas el proceso
    # chrome_options.add_argument("--headless")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Selenium configurado correctamente")
        return driver
        
    except Exception as e:
        print(f"❌ Error configurando Selenium: {str(e)}")
        return None

def hacer_login_linkedin(driver, email, password):
    """
    Hace login en LinkedIn
    """
    try:
        print("🔐 Iniciando sesión en LinkedIn...")
        driver.get("https://www.linkedin.com/login")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        
        print("📝 Ingresando credenciales...")
        
        email_field = driver.find_element(By.ID, "username")
        email_field.clear()
        email_field.send_keys(email)
        
        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(password)
        
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        print("⏳ Esperando respuesta del login...")
        
        try:
            WebDriverWait(driver, 30).until(
                lambda d: "feed" in d.current_url or "in/" in d.current_url or "mynetwork" in d.current_url
            )
            print("✅ Login exitoso!")
            return True
            
        except TimeoutException:
            if "challenge" in driver.page_source.lower():
                print("🤖 LinkedIn requiere verificación (captcha)")
                print("👀 Por favor, completa el captcha manualmente en el navegador")
                input("Presiona Enter cuando hayas completado el captcha...")
                
                WebDriverWait(driver, 30).until(
                    lambda d: "feed" in d.current_url or "in/" in d.current_url
                )
                print("✅ Verificación completada!")
                return True
            else:
                print("❌ Error en el login")
                return False
        
    except Exception as e:
        print(f"❌ Error durante el login: {str(e)}")
        return False

def extraer_informacion_personal(driver):
    """
    Extrae información personal del perfil
    """
    info_personal = {}
    
    try:
        # Nombre
        name_element = driver.find_element(By.CSS_SELECTOR, "h1")
        info_personal["nombre"] = name_element.text.strip()
        print(f"👤 Nombre: {info_personal['nombre']}")
    except:
        print("⚠️ No se pudo extraer el nombre")
    
    try:
        # Título profesional - múltiples selectores
        title_selectors = [
            ".text-body-medium",
            ".top-card-layout__headline",
            ".pv-text-details__left-panel .text-body-medium"
        ]
        
        for selector in title_selectors:
            try:
                title_element = driver.find_element(By.CSS_SELECTOR, selector)
                info_personal["titulo"] = title_element.text.strip()
                print(f"💼 Título: {info_personal['titulo']}")
                break
            except:
                continue
    except:
        print("⚠️ No se pudo extraer el título")
    
    try:
        # Ubicación - múltiples selectores
        location_selectors = [
            ".text-body-small",
            ".top-card__subline-item",
            ".pv-text-details__left-panel .text-body-small"
        ]
        
        for selector in location_selectors:
            try:
                location_element = driver.find_element(By.CSS_SELECTOR, selector)
                info_personal["ubicacion"] = location_element.text.strip()
                print(f"📍 Ubicación: {info_personal['ubicacion']}")
                break
            except:
                continue
    except:
        print("⚠️ No se pudo extraer la ubicación")
    
    # Extraer información "Acerca de"
    try:
        print("📖 Buscando información de 'Acerca de'...")
        acerca_selectors = [
            "#about",
            "section.artdeco-card #about",
            ".pv-profile-section p"
        ]
        
        for selector in acerca_selectors:
            try:
                # Buscar sección de "Acerca de"
                acerca_section = driver.find_element(By.CSS_SELECTOR, selector)
                
                # Buscar el texto del párrafo
                parrafos = acerca_section.find_elements(By.TAG_NAME, "p")
                if parrafos:
                    # Tomar el primero que tenga contenido significativo
                    for parrafo in parrafos:
                        texto = parrafo.text.strip()
                        if texto and len(texto) > 10:
                            info_personal["acerca_de"] = texto
                            print(f"📝 Acerca de: {texto[:100]}...")
                            break
                    break
            except:
                continue
    except Exception as e:
        print(f"⚠️ No se pudo extraer 'Acerca de': {str(e)}")
    
    return info_personal

def extraer_experiencia_linkedin(driver):
    """
    Extrae experiencia basándose en la estructura HTML real de LinkedIn
    """
    experiencias = []
    
    try:
        print("🔍 Buscando sección de experiencia...")
        
        # Buscar la sección de experiencia por el ID
        exp_section = driver.find_element(By.ID, "experience")
        print("✅ Sección de experiencia encontrada")
        
        # Scroll a la sección
        driver.execute_script("arguments[0].scrollIntoView();", exp_section)
        time.sleep(2)
        
        # Buscar todos los elementos li que contienen experiencia
        # La estructura: el anchor está dentro de un li.artdeco-list__item
        exp_items = driver.find_elements(By.CSS_SELECTOR, "#experience ~ .artdeco-card li.artdeco-list__item")
        
        # Si no encuentra, probar otro selector
        if not exp_items or len(exp_items) == 0:
            # Buscar por XPath: elementos li que tienen un anchor con id="experience" en el mismo section
            exp_items = driver.find_elements(By.XPATH, "//section[descendant::div[@id='experience']]//li[contains(@class, 'artdeco-list__item')]")
        
        print(f"📋 Encontrados {len(exp_items)} elementos de experiencia")
        
        for i, item in enumerate(exp_items):
            try:
                # Obtener todo el texto del elemento
                texto_completo = item.text
                
                if not texto_completo or len(texto_completo) < 10 or "Experiencia" in texto_completo:
                    continue
                
                print(f"  📄 Procesando elemento {i+1}:")
                print(f"  Texto completo: {texto_completo[:150]}...")
                
                experiencia = {}
                lineas = [line.strip() for line in texto_completo.split('\n') if line.strip()]
                
                # La primera línea suele ser la empresa
                if len(lineas) > 0:
                    experiencia["empresa"] = lineas[0]
                    print(f"  🏢 Empresa: {lineas[0]}")
                
                # La segunda línea puede ser el título o la duración
                if len(lineas) > 1:
                    if any(p in lineas[1].lower() for p in ["año", "mes", "actualidad"]):
                        experiencia["fechas"] = lineas[1]
                        print(f"  📅 Fechas: {lineas[1]}")
                    else:
                        experiencia["titulo"] = lineas[1]
                        print(f"  💼 Título: {lineas[1]}")
                
                # Buscar fechas en las líneas
                for linea in lineas:
                    if any(palabra in linea for palabra in ["año", "mes", "actualidad", "2024", "2023", "ago.", "sept."]):
                        if not experiencia.get("fechas"):
                            experiencia["fechas"] = linea
                            print(f"  📅 Fechas: {linea}")
                        break
                
                # Buscar ubicación
                for linea in lineas:
                    if any(palabra in linea for palabra in ["Argentina", "Buenos Aires", "Provincia", "Híbrido", "Remoto"]):
                        experiencia["ubicacion"] = linea
                        print(f"  📍 Ubicación: {linea}")
                        break
                
                # Descripción: texto largo o múltiples líneas
                descripcion = "\n".join([linea for linea in lineas if len(linea) > 50])
                if descripcion:
                    experiencia["descripcion"] = descripcion
                    print(f"  📝 Descripción: {descripcion[:80]}...")
                
                # Solo agregar si tenemos información útil
                if experiencia and (experiencia.get("empresa") or experiencia.get("titulo")):
                    experiencias.append(experiencia)
                    print(f"  ✅ Experiencia {len(experiencias)} extraída correctamente")
                
            except Exception as e:
                print(f"  ⚠️ Error extrayendo experiencia {i+1}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"🎯 Total de experiencias extraídas: {len(experiencias)}")
        
    except Exception as e:
        print(f"❌ Error extrayendo experiencia: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return experiencias

def extraer_educacion_linkedin(driver):
    """
    Extrae educación basándose en la estructura HTML real de LinkedIn
    """
    educaciones = []
    
    try:
        print("🔍 Buscando sección de educación...")
        
        # Buscar la sección de educación
        edu_section = driver.find_element(By.ID, "education")
        print("✅ Sección de educación encontrada")
        
        # Scroll a la sección
        driver.execute_script("arguments[0].scrollIntoView();", edu_section)
        time.sleep(2)
        
        # Buscar elementos de educación
        edu_items = driver.find_elements(By.XPATH, "//section[descendant::div[@id='education']]//li[contains(@class, 'artdeco-list__item')]")
        
        print(f"📋 Encontrados {len(edu_items)} elementos de educación")
        
        for item in edu_items:
            try:
                texto_completo = item.text
                
                if not texto_completo or len(texto_completo) < 10 or "Educación" in texto_completo:
                    continue
                
                print(f"  📄 Procesando: {texto_completo[:100]}...")
                
                educacion = {}
                lineas = [line.strip() for line in texto_completo.split('\n') if line.strip()]
                
                # La primera línea suele ser la institución
                if len(lineas) > 0:
                    educacion["institucion"] = lineas[0]
                    print(f"  🎓 Institución: {lineas[0]}")
                
                # La segunda línea puede ser el grado/carrera
                if len(lineas) > 1:
                    educacion["grado"] = lineas[1]
                    print(f"  📚 Grado: {lineas[1]}")
                
                # Buscar fechas
                for linea in lineas:
                    if any(palabra in linea for palabra in ["año", "mes", "actualidad", "2024", "2023", "ago.", "sept."]):
                        educacion["fechas"] = linea
                        print(f"  📅 Fechas: {linea}")
                        break
                
                # Buscar calificaciones
                for linea in lineas:
                    if any(palabra in linea.lower() for palabra in ["promedio", "gpa", "mencion", "honor"]):
                        educacion["calificaciones"] = linea
                        print(f"  📊 Calificaciones: {linea}")
                        break
                
                if educacion and educacion.get("institucion"):
                    educaciones.append(educacion)
                    print(f"  ✅ Educación {len(educaciones)} extraída correctamente")
                
            except Exception as e:
                print(f"  ⚠️ Error extrayendo educación: {str(e)}")
                continue
        
        print(f"🎯 Total de educaciones extraídas: {len(educaciones)}")
        
    except Exception as e:
        print(f"❌ Error extrayendo educación: {str(e)}")
    
    return educaciones

def extraer_licencias_certificaciones_linkedin(driver):
    """
    Extrae licencias y certificaciones basándose en la estructura HTML real de LinkedIn
    """
    licencias = []
    
    try:
        print("🔍 Buscando sección de licencias y certificaciones...")
        
        # Buscar la sección de licencias y certificaciones
        lic_section = driver.find_element(By.ID, "licenses_and_certifications")
        print("✅ Sección de licencias y certificaciones encontrada")
        
        # Scroll a la sección
        driver.execute_script("arguments[0].scrollIntoView();", lic_section)
        time.sleep(2)
        
        # Buscar elementos
        lic_items = driver.find_elements(By.XPATH, "//section[descendant::div[@id='licenses_and_certifications']]//li[contains(@class, 'artdeco-list__item')]")
        
        print(f"📋 Encontrados {len(lic_items)} elementos de licencias y certificaciones")
        
        for item in lic_items:
            try:
                texto_completo = item.text
                
                if not texto_completo or len(texto_completo) < 5 or "licencias" in texto_completo.lower():
                    continue
                
                print(f"  📄 Procesando: {texto_completo[:100]}...")
                
                licencia = {}
                lineas = [line.strip() for line in texto_completo.split('\n') if line.strip()]
                
                # La primera línea suele ser el nombre de la certificación
                if len(lineas) > 0:
                    licencia["nombre"] = lineas[0]
                    print(f"  🎓 Certificado: {lineas[0]}")
                
                # La segunda línea puede ser la organización emisora
                if len(lineas) > 1:
                    licencia["organizacion"] = lineas[1]
                    print(f"  🏢 Organización: {lineas[1]}")
                
                # Buscar fecha de emisión
                for linea in lineas:
                    if any(palabra in linea for palabra in ["2024", "2023", "mar.", "abr.", "jul.", "nov.", "dic."]):
                        licencia["fecha_emision"] = linea
                        print(f"  📅 Fecha: {linea}")
                        break
                
                # Buscar ID de credencial
                for linea in lineas:
                    if "ID" in linea or "Credential" in linea:
                        licencia["id_credencial"] = linea
                        print(f"  🔑 ID: {linea}")
                        break
                
                if licencia and licencia.get("nombre"):
                    licencias.append(licencia)
                    print(f"  ✅ Certificado {len(licencias)} extraído correctamente")
                
            except Exception as e:
                print(f"  ⚠️ Error extrayendo licencia: {str(e)}")
                continue
        
        print(f"🎯 Total de licencias y certificaciones extraídas: {len(licencias)}")
        
    except Exception as e:
        print(f"❌ Error extrayendo licencias y certificaciones: {str(e)}")
    
    return licencias

def main():
    """
    Función principal
    """
    print("🚀 LINKEDIN SCRAPING MEJORADO")
    print("=" * 60)
    
    # Credenciales
    email = "phishintel02@gmail.com"
    password = "Phishintel2025."
    
    print(f"📧 Email: {email}")
    print(f"🔒 Password: [OCULTO]")
    print()
    
    # Configurar driver
    driver = setup_selenium_driver()
    if not driver:
        return
    
    try:
        # Hacer login
        if not hacer_login_linkedin(driver, email, password):
            print("❌ No se pudo hacer login")
            return
        
        print()
        
        # Ir al perfil de Ignacio
        perfil_url = "https://www.linkedin.com/in/ignacio-piloni/"
        print(f"🔍 Accediendo a perfil: {perfil_url}")
        
        driver.get(perfil_url)
        
        # Esperar a que la página cargue
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print("✅ Perfil cargado correctamente")
        print()
        
        # Extraer información completa
        info = {
            "informacion_personal": {},
            "experiencia": [],
            "educacion": [],
            "licencias_certificaciones": []
        }
        
        # Información personal
        print("👤 EXTRAYENDO INFORMACIÓN PERSONAL...")
        info["informacion_personal"] = extraer_informacion_personal(driver)
        print()
        
        # Experiencia
        print("💼 EXTRAYENDO EXPERIENCIA...")
        info["experiencia"] = extraer_experiencia_linkedin(driver)
        print()
        
        # Educación
        print("🎓 EXTRAYENDO EDUCACIÓN...")
        info["educacion"] = extraer_educacion_linkedin(driver)
        print()
        
        # Licencias y Certificaciones
        print("📜 EXTRAYENDO LICENCIAS Y CERTIFICACIONES...")
        info["licencias_certificaciones"] = extraer_licencias_certificaciones_linkedin(driver)
        print()
        
        # Mostrar resumen completo
        print("=" * 60)
        print("✅ EXTRACCIÓN COMPLETA FINALIZADA")
        print("=" * 60)
        
        if info["informacion_personal"]:
            print("👤 INFORMACIÓN PERSONAL:")
            for key, value in info["informacion_personal"].items():
                if key == "acerca_de" and isinstance(value, str) and len(value) > 100:
                    print(f"  • {key.replace('_', ' ').title()}: {value[:100]}...")
                else:
                    print(f"  • {key.replace('_', ' ').title()}: {value}")
            print()
        
        if info["experiencia"]:
            print(f"💼 EXPERIENCIA ({len(info['experiencia'])} trabajos):")
            for i, exp in enumerate(info["experiencia"], 1):
                print(f"  {i}. {exp.get('titulo', 'N/A')} en {exp.get('empresa', 'N/A')}")
                if exp.get('fechas'):
                    print(f"     📅 {exp['fechas']}")
                if exp.get('ubicacion'):
                    print(f"     📍 {exp['ubicacion']}")
                if exp.get('descripcion'):
                    print(f"     📝 {exp['descripcion'][:100]}...")
                if exp.get('habilidades_relacionadas'):
                    print(f"     🛠️ {exp['habilidades_relacionadas']}")
                print()
        
        if info["educacion"]:
            print(f"🎓 EDUCACIÓN ({len(info['educacion'])} estudios):")
            for i, edu in enumerate(info["educacion"], 1):
                print(f"  {i}. {edu.get('grado', 'N/A')} - {edu.get('institucion', 'N/A')}")
                if edu.get('fechas'):
                    print(f"     📅 {edu['fechas']}")
                if edu.get('calificaciones'):
                    print(f"     📊 {edu['calificaciones']}")
                print()
        
        if info["licencias_certificaciones"]:
            print(f"📜 LICENCIAS Y CERTIFICACIONES ({len(info['licencias_certificaciones'])}):")
            for i, lic in enumerate(info["licencias_certificaciones"], 1):
                print(f"  {i}. {lic.get('nombre', 'N/A')}")
                if lic.get('organizacion'):
                    print(f"     🏢 {lic['organizacion']}")
                if lic.get('fecha_emision'):
                    print(f"     📅 {lic['fecha_emision']}")
                if lic.get('id_credencial'):
                    print(f"     🔑 {lic['id_credencial']}")
                print()
        
        # Guardar resultado completo
        with open('../ignacio_cv_completo.json', 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        print("💾 Resultado completo guardado en: ignacio_cv_completo.json")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Proceso cancelado por el usuario")
    
    except Exception as e:
        print(f"\n❌ Error crítico: {str(e)}")
    
    finally:
        print("\n🔚 Cerrando navegador...")
        driver.quit()

if __name__ == "__main__":
    main()
