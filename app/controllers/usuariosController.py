from flask import jsonify
from app.backend.models import Usuario
from app.backend.models.error import responseError
from app.config.db_config import SessionLocal
from app.utils.hash import hash_password

class UsuariosController:

    @staticmethod
    def obtenerUsuario(idUsuario):
        session = SessionLocal()
        usuario = session.query(Usuario).filter_by(idUsuario=idUsuario).first()
        session.close()
        if usuario is None:
            return responseError("USUARIO_NO_ENCONTRADO", "El usuario no existe", 404)

        return jsonify(usuario.get()), 200

    @staticmethod
    def obtenerUsuarios():
        session = SessionLocal()
        usuarios = session.query(Usuario)
        session.close()
        usuariosARetornar = [usuario.get() for usuario in usuarios]
        return jsonify({"usuarios": usuariosARetornar}), 200

    @staticmethod
    def crearUsuario(data):
        if not data or "idUsuario" not in data or "password" not in data or "nombre" not in data or "apellido" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios para crear el usuario", 400)

        session = SessionLocal()
        usuarioExistente = session.query(Usuario).filter_by(idUsuario=data["idUsuario"]).first()

        if usuarioExistente is not None:
            session.close()
            return responseError("USUARIO_YA_EXSITE", "El usuario ya existe", 400)

        hashedPassword = hash_password(data["password"])

        nuevoUsuario = Usuario(idUsuario=data["idUsuario"],
                               password=hashedPassword,
                               nombre=data["nombre"],
                               apellido=data["apellido"])

        session.add(nuevoUsuario)
        session.commit()
        session.refresh(nuevoUsuario)
        session.close()

        return jsonify({"mensaje": "Usuario creado correctamente"}), 201

    @staticmethod
    def eliminarUsuario(idUsuario):
        session = SessionLocal()

        usuario = session.query(Usuario).filter_by(idUsuario=idUsuario).first()

        if not usuario:
            session.close()
            return responseError("USUARIO_NO_ENCONTRADO", "El usuario no existe", 404)

        session.delete(usuario)
        session.commit()
        session.close()

        return jsonify({"mensaje": "Usuario eliminado correctamente"}), 200