from enum import Enum

class EstadoReporte(Enum):
    PENDIENTE = "PENDIENTE"
    VERIFICADO = "VERIFICADO"
    RECHAZADO = "RECHAZADO"
    VALIDADO_SIN_EVENTO = "VALIDADO_SIN_EVENTO"  # Validado aunque no tenga evento asociado
