import enum

class TipoEvento(enum.Enum):
    LLAMADA_SMS = "LLAMADA_SMS" # Llamada + SMS
    LLAMADA_WPP = "LLAMADA_WPP" # Llamada + WPP
    LLAMADA_CORREO = "LLAMADA_CORREO" # Llamada + Correo
    LLAMADA = "LLAMADA" # Llamada simple (Para pedir información o algo por el estilo, por favor no borrar)
    VIDEOLLAMADA = "VIDEOLLAMADA" 
    CORREO = "CORREO" # Correo simple (Un correo llega a tu casilla)
    MENSAJE = "MENSAJE" # Mensaje simple (Un mensaje llega a tu casilla, puede ser tanto SMS como WPP)
