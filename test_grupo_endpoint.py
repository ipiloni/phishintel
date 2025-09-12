#!/usr/bin/env python3
"""
Script de prueba para el nuevo endpoint de mensajes a grupos de WhatsApp
"""

import requests
import json

def test_grupo_endpoint():
    """Prueba el endpoint de envío de mensajes a grupos"""
    
    # URL del endpoint
    url = "http://localhost:8080/api/mensajes/whatsapp-grupo-whapi"
    
    # Datos de prueba
    test_data = {
        "mensaje": "¡Hola grupo! Este es un mensaje de prueba desde PhishIntel API 🚀",
        "grupo_id": "Proyecto Grupo 8 🤝🏻✨🎉🙌🏻"
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🧪 Probando endpoint de mensajes a grupos...")
        print(f"📤 Enviando mensaje: {test_data['mensaje']}")
        print(f"👥 Al grupo: {test_data['grupo_id']}")
        
        # Realizar la petición
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        
        print(f"\n📊 Respuesta del servidor:")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ ¡Mensaje enviado exitosamente!")
            response_data = response.json()
            print(f"📝 Respuesta: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        else:
            print("❌ Error al enviar mensaje")
            print(f"📝 Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. Asegúrate de que la API esté ejecutándose en localhost:8080")
    except requests.exceptions.Timeout:
        print("❌ Error: Timeout al enviar la petición")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    test_grupo_endpoint()
