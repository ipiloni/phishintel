import logging

# Success customizado
SUCCESS_LEVEL_NUM = 25  # Entre INFO y WARNING
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")

def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        # ANSI green color for the text
        message = f"\033[92m{message}\033[0m"
        self._log(SUCCESS_LEVEL_NUM, message, args, **kwargs)

logging.Logger.success = success

# Configuración básica del logger
logging.basicConfig(
    level=logging.INFO,  # Nivel mínimo a registrar (INFO, WARNING, ERROR, etc.)
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

log = logging.getLogger("PhishIntel")