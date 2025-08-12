import logging

# Configuración básica del logger
logging.basicConfig(
    level=logging.INFO,  # Nivel mínimo a registrar (INFO, WARNING, ERROR, etc.)
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

log = logging.getLogger("PhishIntel")