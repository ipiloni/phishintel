import enum

class TipoEvento(enum.Enum):
    LLAMADA = "LLAMADA"
    CORREO = "CORREO"
    MENSAJE = "MENSAJE"
    VIDEOLLAMADA = "VIDEOLLAMADA"