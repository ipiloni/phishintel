from flask import Flask
from app.config.db_config import Base, engine
from app.frontend import frontend
from app.apis import apis
from app.swagger import swagger

app = Flask(__name__)
Base.metadata.create_all(engine)

# Registro de blueprints
app.register_blueprint(apis)
app.register_blueprint(frontend)
app.register_blueprint(swagger)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
