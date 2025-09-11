from flask import jsonify
from app.backend.models import Usuario, UsuarioxEvento
from app.backend.models.area import Area
from app.backend.models.error import responseError
from app.config.db_config import SessionLocal
from app.utils.hash import hash_password

class UsuariosController:

    @staticmethod
    def _serialize_usuario(usuario, exclude=None):
        import datetime, enum
        exclude = set(exclude or [])
        data = {}
        for col in usuario.__table__.columns:
            name = col.name
            if name in exclude:
                continue
            val = getattr(usuario, name)
            if val is None:
                data[name] = None
            elif isinstance(val, enum.Enum):
                data[name] = val.value
            elif isinstance(val, (datetime.date, datetime.datetime)):
                data[name] = val.isoformat()
            else:
                data[name] = val
        return data

    @staticmethod
    def obtenerUsuario(idUsuario):
        session = SessionLocal()
        try:
            usuario = session.query(Usuario).filter_by(idUsuario=idUsuario).first()
            if usuario is None:
                return responseError("USUARIO_NO_ENCONTRADO", "El usuario no existe", 404)

            usuario_dict = UsuariosController._serialize_usuario(usuario, exclude=["password"])
            return jsonify(usuario_dict), 200
        finally:
            session.close()

    @staticmethod
    def obtenerTodosLosUsuarios():
        session = SessionLocal()
        try:
            usuarios = session.query(Usuario).all()  # <- .all() para traer la lista antes de cerrar la sesión
            usuariosARetornar = [
                UsuariosController._serialize_usuario(u, exclude=["password"]) for u in usuarios
            ]
            return jsonify({"usuarios": usuariosARetornar}), 200
        finally:
            session.close()

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
    def crearUsuariosBatch(payload):
        if not payload:
            return responseError("CAMPOS_OBLIGATORIOS", "Se requiere un cuerpo con 'usuarios'", 400)

        usuarios_data = payload if isinstance(payload, list) else payload.get("usuarios")
        if not isinstance(usuarios_data, list):
            return responseError("CAMPOS_OBLIGATORIOS", "'usuarios' debe ser una lista", 400)

        session = SessionLocal()
        resultados = []
        try:
            for idx, data in enumerate(usuarios_data):
                try:
                    if not data or "nombreUsuario" not in data or "password" not in data or "nombre" not in data or "apellido" not in data:
                        resultados.append({"index": idx, "ok": False, "error": "Faltan campos obligatorios"})
                        continue

                    existente = session.query(Usuario).filter_by(nombreUsuario=data["nombreUsuario"]).first()
                    if existente is not None:
                        resultados.append({"index": idx, "ok": False, "error": f"Usuario ya existe id={existente.idUsuario}"})
                        continue

                    hashed = hash_password(data["password"])
                    nuevo = Usuario(
                        nombreUsuario=data["nombreUsuario"],
                        password=hashed,
                        nombre=data["nombre"],
                        apellido=data["apellido"],
                        telefono=data.get("telefono"),
                        correo=data.get("correo"),
                        direccion=data.get("direccion"),
                        esAdministrador=data.get("esAdministrador"),
                        idArea=data.get("idArea")
                    )
                    if data.get("esAdministrador") is None:
                        nuevo.esAdministrador = False

                    session.add(nuevo)
                    session.flush()
                    resultados.append({"index": idx, "ok": True, "idUsuario": nuevo.idUsuario})
                except Exception as e:
                    resultados.append({"index": idx, "ok": False, "error": str(e)})

            session.commit()
            ok_count = sum(1 for r in resultados if r.get("ok"))
            return jsonify({"creados": ok_count, "resultados": resultados}), 201
        except Exception as e:
            session.rollback()
            return responseError("ERROR", f"No se pudo crear el batch: {str(e)}", 500)
        finally:
            session.close()

    @staticmethod
    def eliminarUsuario(idUsuario):
        session = SessionLocal()
        try:
            usuario = session.query(Usuario).filter_by(idUsuario=idUsuario).first()

            if not usuario:
                return responseError("USUARIO_NO_ENCONTRADO", "El usuario no existe", 404)

            # Borrar asociaciones usuarioxevento
            session.query(UsuarioxEvento).filter_by(idUsuario=idUsuario).delete()

            # Borrar usuario
            session.delete(usuario)
            session.commit()
            return jsonify({"mensaje": "Usuario eliminado correctamente"}), 200
        except Exception as e:
            session.rollback()
            return responseError("ERROR", f"No se pudo eliminar el usuario: {str(e)}", 500)
        finally:
            session.close()

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
        if "idArea" in data:
            usuario.idArea = data["idArea"]

        session.commit()
        session.close()

        return jsonify({"mensaje": "Usuario actualizado correctamente"}), 200
