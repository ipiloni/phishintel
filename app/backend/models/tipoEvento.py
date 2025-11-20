import enum

class TipoEvento(enum.Enum):
    LLAMADA = "LLAMADA" # Llamada simple (Para pedir información o algo por el estilo, por favor no borrar)
    CORREO = "CORREO" # Correo simple (Un correo llega a tu casilla)
    MENSAJE = "MENSAJE" # Mensaje simple (Un mensaje llega a tu casilla, puede ser tanto SMS como WPP)
