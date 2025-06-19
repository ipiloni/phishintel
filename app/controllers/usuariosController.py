from flask import jsonify, request
from app.main import app
from app.backend.models import Usuario
from app.backend.models.error import responseError
from app.config.db_config import SessionLocal

@app.route("/usuarios", methods=["POST"])
def crearUsuario():
    data = request.get_json()

    if not data or "idUsuario" not in data or "password" not in data or "nombre" not in data or "apellido" not in data:
        return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios para crear el usuario", 400)

    nuevoUsuario = Usuario(idUsuario = data["idUsuario"], password = data["password"], nombre = data["nombre"], apellido = data["apellido"])

    session = SessionLocal()
    session.add(nuevoUsuario)
    session.commit()
    session.refresh(nuevoUsuario)
    session.close()

    return jsonify({"mensaje": "Usuario creado correctamente"}), 201