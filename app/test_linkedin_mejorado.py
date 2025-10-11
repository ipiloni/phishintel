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
        time.sleep(3)
        
        # Buscar los elementos de experiencia usando la estructura real
        # Cada trabajo está en un li con clase específica
        exp_items = driver.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")
        
        print(f"📋 Encontrados {len(exp_items)} elementos de experiencia")
        
        for i, item in enumerate(exp_items):
            try:
                # Verificar si este elemento contiene información de experiencia
                # Buscar el patrón específico de LinkedIn
                empresa_elements = item.find_elements(By.CSS_SELECTOR, ".hoverable-link-text.t-bold span[aria-hidden='true']")
                titulo_elements = item.find_elements(By.CSS_SELECTOR, ".hoverable-link-text.t-bold span[aria-hidden='true']")
                
                if not empresa_elements:
                    continue
                
                experiencia = {}
                
                # Extraer empresa (primer elemento)
                if len(empresa_elements) > 0:
                    empresa_text = empresa_elements[0].text.strip()
                    if empresa_text and empresa_text not in ["Experiencia"]:  # Filtrar el título de la sección
                        experiencia["empresa"] = empresa_text
                        print(f"  🏢 Empresa: {empresa_text}")
                
                # Extraer título del trabajo (segundo elemento si existe)
                if len(titulo_elements) > 1:
                    titulo_text = titulo_elements[1].text.strip()
                    if titulo_text and titulo_text != experiencia.get("empresa", ""):
                        experiencia["titulo"] = titulo_text
                        print(f"  💼 Título: {titulo_text}")
                
                # Extraer fechas
                try:
                    fecha_elements = item.find_elements(By.CSS_SELECTOR, ".pvs-entity__caption-wrapper span[aria-hidden='true']")
                    if fecha_elements:
                        fecha_text = fecha_elements[0].text.strip()
                        experiencia["fechas"] = fecha_text
                        print(f"  📅 Fechas: {fecha_text}")
                except:
                    pass
                
                # Extraer ubicación
                try:
                    ubicacion_elements = item.find_elements(By.CSS_SELECTOR, ".t-14.t-normal.t-black--light span[aria-hidden='true']")
                    for elem in ubicacion_elements:
                        ubicacion_text = elem.text.strip()
                        if "Argentina" in ubicacion_text or "Buenos Aires" in ubicacion_text:
                            experiencia["ubicacion"] = ubicacion_text
                            print(f"  📍 Ubicación: {ubicacion_text}")
                            break
                except:
                    pass
                
                # Extraer descripción
                try:
                    desc_elements = item.find_elements(By.CSS_SELECTOR, ".inline-show-more-text--is-collapsed span[aria-hidden='true']")
                    if desc_elements:
                        desc_text = desc_elements[0].text.strip()
                        experiencia["descripcion"] = desc_text
                        print(f"  📝 Descripción: {desc_text[:100]}...")
                except:
                    pass
                
                # Extraer habilidades relacionadas
                try:
                    skills_elements = item.find_elements(By.CSS_SELECTOR, ".hoverable-link-text.t-14.t-normal.t-black strong")
                    if skills_elements:
                        skills_text = skills_elements[0].text.strip()
                        experiencia["habilidades_relacionadas"] = skills_text
                        print(f"  🛠️ Habilidades: {skills_text}")
                except:
                    pass
                
                # Solo agregar si tenemos información útil
                if experiencia and (experiencia.get("empresa") or experiencia.get("titulo")):
                    experiencias.append(experiencia)
                    print(f"  ✅ Experiencia {len(experiencias)} extraída correctamente")
                
            except Exception as e:
                print(f"  ⚠️ Error extrayendo experiencia {i+1}: {str(e)}")
                continue
        
        print(f"🎯 Total de experiencias extraídas: {len(experiencias)}")
        
    except Exception as e:
        print(f"❌ Error extrayendo experiencia: {str(e)}")
    
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
        time.sleep(3)
        
        # Buscar elementos de educación
        edu_items = driver.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")
        
        for item in edu_items:
            try:
                educacion = {}
                
                # Buscar institución
                institucion_elements = item.find_elements(By.CSS_SELECTOR, ".hoverable-link-text.t-bold span[aria-hidden='true']")
                if institucion_elements:
                    institucion_text = institucion_elements[0].text.strip()
                    if institucion_text and institucion_text not in ["Educación"]:
                        educacion["institucion"] = institucion_text
                        print(f"  🎓 Institución: {institucion_text}")
                
                # Buscar grado/carrera
                if len(institucion_elements) > 1:
                    grado_text = institucion_elements[1].text.strip()
                    if grado_text and grado_text != educacion.get("institucion", ""):
                        educacion["grado"] = grado_text
                        print(f"  📚 Grado: {grado_text}")
                
                # Buscar fechas
                fecha_elements = item.find_elements(By.CSS_SELECTOR, ".pvs-entity__caption-wrapper span[aria-hidden='true']")
                if fecha_elements:
                    fecha_text = fecha_elements[0].text.strip()
                    educacion["fechas"] = fecha_text
                    print(f"  📅 Fechas: {fecha_text}")
                
                if educacion and educacion.get("institucion"):
                    educaciones.append(educacion)
                
            except:
                continue
        
        print(f"🎯 Total de educaciones extraídas: {len(educaciones)}")
        
    except Exception as e:
        print(f"❌ Error extrayendo educación: {str(e)}")
    
    return educaciones

def extraer_habilidades_linkedin(driver):
    """
    Extrae habilidades basándose en la estructura HTML real de LinkedIn
    """
    habilidades = []
    
    try:
        print("🔍 Buscando sección de habilidades...")
        
        # Buscar la sección de habilidades
        skills_section = driver.find_element(By.ID, "skills")
        print("✅ Sección de habilidades encontrada")
        
        # Scroll a la sección
        driver.execute_script("arguments[0].scrollIntoView();", skills_section)
        time.sleep(3)
        
        # Buscar elementos de habilidades
        skill_elements = driver.find_elements(By.CSS_SELECTOR, ".skill-category-entity__name")
        
        for skill_elem in skill_elements:
            try:
                skill_text = skill_elem.text.strip()
                if skill_text:
                    habilidades.append(skill_text)
            except:
                continue
        
        print(f"🎯 Total de habilidades extraídas: {len(habilidades)}")
        
    except Exception as e:
        print(f"❌ Error extrayendo habilidades: {str(e)}")
    
    return habilidades

def main():
    """
    Función principal
    """
    print("🚀 LINKEDIN SCRAPING MEJORADO")
    print("=" * 60)
    
    # Credenciales
    email = "phishingintel@gmail.com"
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
            "habilidades": []
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
        
        # Habilidades
        print("🛠️ EXTRAYENDO HABILIDADES...")
        info["habilidades"] = extraer_habilidades_linkedin(driver)
        print()
        
        # Mostrar resumen completo
        print("=" * 60)
        print("✅ EXTRACCIÓN COMPLETA FINALIZADA")
        print("=" * 60)
        
        if info["informacion_personal"]:
            print("👤 INFORMACIÓN PERSONAL:")
            for key, value in info["informacion_personal"].items():
                print(f"  • {key.title()}: {value}")
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
                print()
        
        if info["habilidades"]:
            print(f"🛠️ HABILIDADES ({len(info['habilidades'])}):")
            print(f"  {', '.join(info['habilidades'])}")
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
