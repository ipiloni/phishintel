from flask import Flask
from app.config.db_config import Base, engine
from app.endpoints.frontend import frontend
from app.endpoints.apis import apis
from app.endpoints.swagger import swagger
from dotenv import load_dotenv
import os

# Importar modelos para que se registren en Base.metadata
from app.backend.models import TelethonSession  # noqa: F401

load_dotenv(dotenv_path="properties.env")

app = Flask(__name__)

# Configuración de sesión
app.secret_key = os.environ.get('SECRET_KEY', 'phishintel-secret-key-change-in-production')

Base.metadata.create_all(engine)

# Registro de blueprints
app.register_blueprint(apis)
app.register_blueprint(frontend)
app.register_blueprint(swagger)

if __name__ == "__main__":
    load_dotenv(dotenv_path="properties.env")
    app.run(debug=True, port=8080)
