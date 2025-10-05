import enum

class TipoEvento(enum.Enum):
    LLAMADA_SMS = "LLAMADA_SMS"
    LLAMADA_WPP = "LLAMADA_WPP"
    LLAMADA_CORREO = "LLAMADA_CORREO"
    CORREO = "CORREO"
    MENSAJE = "MENSAJE"
