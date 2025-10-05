from flask import jsonify, request, redirect, url_for, session
from sqlalchemy.orm import Session
from app.config.db_config import SessionLocal
from app.backend.models import Usuario
from app.utils.hash import check_password  # función que compara hash vs texto plano

class AuthController:

    @staticmethod
    def login(data):
        if not data or "email" not in data or "password" not in data:
            return jsonify({"error": "Faltan campos obligatorios"}), 400

        session_db: Session = SessionLocal()
        usuario = session_db.query(Usuario).filter_by(correo=data["email"]).first()

        if usuario is None:
            session_db.close()
            return jsonify({"error": "Credenciales inválidas"}), 401

        if not check_password(data["password"], usuario.password):
            session_db.close()
            return jsonify({"error": "Credenciales inválidas"}), 401

        # Guardar información del usuario en la sesión
        session['user_id'] = usuario.idUsuario
        session['user_name'] = f"{usuario.nombre} {usuario.apellido}"
        session['user_email'] = usuario.correo
        session['is_admin'] = usuario.esAdministrador or False
        
        session_db.close()
        
        # Determinar redirección basada en si es administrador
        redirect_url = "/principal" if usuario.esAdministrador else "/principalEmpleado"
        
        # ✅ si todo bien devolvemos OK
        return jsonify({
            "mensaje": "Login exitoso", 
            "redirect": redirect_url,
            "usuario": {
                "id": usuario.idUsuario,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "email": usuario.correo,
                "esAdministrador": usuario.esAdministrador
            }
        }), 200

    @staticmethod
    def logout():
        """Cerrar sesión del usuario"""
        session.clear()
        return jsonify({"mensaje": "Sesión cerrada exitosamente"}), 200

    @staticmethod
    def get_current_user():
        """Obtener información del usuario actualmente logueado"""
        if 'user_id' not in session:
            return None
        
        session_db: Session = SessionLocal()
        usuario = session_db.query(Usuario).filter_by(idUsuario=session['user_id']).first()
        session_db.close()
        
        if usuario:
            return {
                "id": usuario.idUsuario,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "email": usuario.correo,
                "esAdministrador": usuario.esAdministrador
            }
        return None

    @staticmethod
    def is_logged_in():
        """Verificar si hay un usuario logueado"""
        return 'user_id' in session

    @staticmethod
    def is_admin():
        """Verificar si el usuario logueado es administrador"""
        return session.get('is_admin', False)
