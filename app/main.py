from flask import Flask
from app.config.db_config import Base, engine
from app.endpoints.frontend import frontend
from app.endpoints.apis import apis
from app.endpoints.swagger import swagger
from dotenv import load_dotenv
import os
import atexit

# Importar modelos para que se registren en Base.metadata
from app.backend.models import TelethonSession  # noqa: F401
from app.utils.cloudflare_tunnel import tunnel_manager
from app.utils.logger import log

load_dotenv(dotenv_path="properties.env")

app = Flask(__name__)

# Configuración de sesión
app.secret_key = os.environ.get('SECRET_KEY', 'phishintel-secret-key-change-in-production')

Base.metadata.create_all(engine)

# Registro de blueprints
app.register_blueprint(apis)
app.register_blueprint(frontend)
app.register_blueprint(swagger)

# Registrar función para limpiar el túnel al cerrar la aplicación
atexit.register(tunnel_manager.stop_tunnel)

# Variable para controlar que el túnel solo se inicie una vez
_tunnel_started = False

def print_banner():
    """Imprime el banner ASCII 3D de PhishIntel"""
    banner = """
    ██████╗ ██╗  ██╗██╗███████╗██╗  ██╗██╗███╗   ██╗████████╗███████╗██╗     
    ██╔══██╗██║  ██║██║██╔════╝██║  ██║██║████╗  ██║╚══██╔══╝██╔════╝██║     
    ██████╔╝███████║██║███████╗███████║██║██╔██╗ ██║   ██║   █████╗  ██║     
    ██╔═══╝ ██╔══██║██║╚════██║██╔══██║██║██║╚██╗██║   ██║   ██╔══╝  ██║     
    ██║     ██║  ██║██║███████║██║  ██║██║██║ ╚████║   ██║   ███████╗███████╗
    ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚══════╝
    """
    print(banner)

def init_tunnel():
    """Inicializa el túnel de Cloudflare solo una vez"""
    global _tunnel_started
    if _tunnel_started:
        return
    
    # En modo debug de Flask, WERKZEUG_RUN_MAIN se establece en el proceso hijo
    # Solo ejecutar en el proceso principal o cuando no está en modo debug
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        print_banner()

        log.info("Iniciando aplicación PhishIntel...")
        
        tunnel_started = tunnel_manager.start_tunnel()
        if not tunnel_started:
            log.info("La aplicación se iniciará sin túnel Cloudflare")

        log.info("Iniciando servidor Flask en puerto 8080...")

        _tunnel_started = True

if __name__ == "__main__":
    load_dotenv(dotenv_path="properties.env")
    init_tunnel()
    app.run(debug=True, port=8080)
