from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

engine = create_engine("sqlite:///phishintel.db")
SessionLocal = sessionmaker(bind=engine)

from app.controllers import usuariosController

if __name__ == "__main__":
    app.run(debug=True, port=8080)