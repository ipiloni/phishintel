from flask import jsonify, request, redirect, url_for
from sqlalchemy.orm import Session
from app.config.db_config import SessionLocal
from app.backend.models import Usuario
from app.utils.hash import check_password  # función que compara hash vs texto plano

class AuthController:

    @staticmethod
    def login(data):
        if not data or "email" not in data or "password" not in data:
            return jsonify({"error": "Faltan campos obligatorios"}), 400

        session: Session = SessionLocal()
        usuario = session.query(Usuario).filter_by(correo=data["email"]).first()

        if usuario is None:
            session.close()
            return jsonify({"error": "Credenciales inválidas"}), 401

        if not check_password(data["password"], usuario.password):
            session.close()
            return jsonify({"error": "Credenciales inválidas"}), 401

        session.close()
        # ✅ si todo bien devolvemos OK
        return jsonify({"mensaje": "Login exitoso", "redirect": "/principal"}), 200
