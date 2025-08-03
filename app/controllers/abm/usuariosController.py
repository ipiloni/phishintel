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
        if not data or "nombreUsuario" not in data or "password" not in data or "nombre" not in data or "apellido" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios para crear el usuario", 400)

        session = SessionLocal()
        usuarioExistente = session.query(Usuario).filter_by(nombreUsuario=data["nombreUsuario"]).first()

        if usuarioExistente is not None:
            session.close()
            return responseError("USUARIO_YA_EXSITE", "El usuario ya existe bajo el id=" + str(usuarioExistente.idUsuario), 400)

        hashedPassword = hash_password(data["password"])

        nuevoUsuario = Usuario(nombreUsuario=data["nombreUsuario"],
                               password=hashedPassword,
                               nombre=data["nombre"],
                               apellido=data["apellido"],
                               telefono=data.get("telefono"),
                               correo=data.get("correo"),
                               direccion=data.get("direccion"),
                               esAdministrador=data.get("esAdministrador"))

        if data.get("esAdministrador") is None:
            nuevoUsuario.esAdministrador = False

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

    @staticmethod
    def editarUsuario(idUsuario, data):
        session = SessionLocal()

        usuario = session.query(Usuario).filter_by(idUsuario=idUsuario).first()

        if not usuario:
            session.close()
            return responseError("USUARIO_NO_ENCONTRADO", "El usuario no existe", 404)

        if "nombreUsuario" in data:
            usuario.nombreUsuario = data.get("nombreUsuario"),
        if "nombre" in data:
            usuario.nombre = data["nombre"]
        if "apellido" in data:
            usuario.apellido = data["apellido"]
        if "direccion" in data:
            usuario.direccion = data["direccion"]
        if "telefono" in data:
            usuario.telefono = data["telefono"]
        if "correo" in data:
            usuario.correo = data["correo"]
        if "esAdministrador" in data:
            usuario.esAdministrador = data["esAdministrador"]

        session.commit()
        session.close()

        return jsonify({"mensaje": "Usuario actualizado correctamente"}), 200