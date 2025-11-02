"""
Utilidades para codificar y decodificar parámetros de URLs de phishing.
Permite encubrir los parámetros para que no sean tan obvios.
"""
import base64
import json
from typing import Dict, Optional

# Mapeo de rutas internas a rutas públicas (más genéricas)
ROUTE_MAPPING = {
    "caiste": "verify",
    "caisteLogin": "auth",
    "caisteDatos": "update"
}

# Mapeo inverso para decodificar
REVERSE_ROUTE_MAPPING = {v: k for k, v in ROUTE_MAPPING.items()}


def encode_phishing_params(id_usuario: int, id_evento: int) -> str:
    """
    Codifica los parámetros idUsuario e idEvento en una cadena base64.
    
    Args:
        id_usuario: ID del usuario
        id_evento: ID del evento
        
    Returns:
        Cadena codificada en base64 que contiene ambos parámetros
    """
    params_dict = {
        "u": id_usuario,  # 'u' en lugar de 'idUsuario'
        "e": id_evento    # 'e' en lugar de 'idEvento'
    }
    params_json = json.dumps(params_dict)
    encoded = base64.urlsafe_b64encode(params_json.encode('utf-8')).decode('utf-8')
    # Remover padding '=' para hacerlo menos obvio
    return encoded.rstrip('=')


def decode_phishing_params(encoded_params: str) -> Optional[Dict[int, int]]:
    """
    Decodifica una cadena base64 para obtener idUsuario e idEvento.
    
    Args:
        encoded_params: Cadena codificada en base64
        
    Returns:
        Diccionario con 'idUsuario' e 'idEvento', o None si hay error
    """
    try:
        # Agregar padding si es necesario
        padding = 4 - (len(encoded_params) % 4)
        if padding != 4:
            encoded_params += '=' * padding
        
        decoded = base64.urlsafe_b64decode(encoded_params.encode('utf-8')).decode('utf-8')
        params_dict = json.loads(decoded)
        
        return {
            "idUsuario": params_dict.get("u"),
            "idEvento": params_dict.get("e")
        }
    except Exception:
        return None


def encode_route(internal_route: str) -> str:
    """
    Convierte una ruta interna a una ruta pública genérica.
    
    Args:
        internal_route: Ruta interna (caiste, caisteLogin, caisteDatos)
        
    Returns:
        Ruta pública genérica (verify, login, update)
    """
    return ROUTE_MAPPING.get(internal_route, internal_route)


def decode_route(public_route: str) -> str:
    """
    Convierte una ruta pública genérica a ruta interna.
    
    Args:
        public_route: Ruta pública genérica (verify, login, update)
        
    Returns:
        Ruta interna (caiste, caisteLogin, caisteDatos)
    """
    return REVERSE_ROUTE_MAPPING.get(public_route, public_route)


def build_phishing_url(base_url: str, route: str, id_usuario: int, id_evento: int) -> str:
    """
    Construye una URL de phishing codificada.
    
    Args:
        base_url: URL base (ej: http://pgcontrol.lat)
        route: Ruta interna (caiste, caisteLogin, caisteDatos)
        id_usuario: ID del usuario
        id_evento: ID del evento
        
    Returns:
        URL codificada con ruta genérica y parámetros codificados
    """
    public_route = encode_route(route)
    encoded_params = encode_phishing_params(id_usuario, id_evento)
    return f"{base_url}/{public_route}?t={encoded_params}"

