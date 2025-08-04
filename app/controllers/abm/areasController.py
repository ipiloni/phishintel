from flask import jsonify
from app.backend.models import Usuario
from app.backend.models.area import Area
from app.backend.models.error import responseError
from app.config.db_config import SessionLocal

class AreasController:

    @staticmethod
    def crearArea(data):

        if not data or "nombreArea" not in data or "usuarios" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios para crear el area", 400)

        session = SessionLocal()
        try:

            areaExistente = session.query(Area).filter_by(nombreArea=data["nombreArea"]).first()

            if areaExistente is not None:
                session.close()
                return responseError("AREA_YA_EXSITE", "El area ya existe bajo el id=" + str(areaExistente.idArea),400)

            # Obtener lista de IDs de usuarios
            usuarios_ids = data["usuarios"]

            if not isinstance(usuarios_ids, list) or not all(isinstance(id, int) for id in usuarios_ids):
                return responseError("USUARIOS_INVALIDOS", "La lista de usuarios debe contener solo IDs numéricos", 400)

            # Buscar usuarios en la base
            usuarios = session.query(Usuario).filter(Usuario.idUsuario.in_(usuarios_ids)).all()

            if len(usuarios) != len(set(usuarios_ids)):
                return responseError("USUARIOS_NO_ENCONTRADOS", "Uno o más usuarios no existen", 404)

            # Crear nueva área
            nuevaArea = Area(
                nombreArea=data["nombreArea"],
                datosDelArea=data.get("datosArea"),
                usuarios=usuarios  # <- relaciona los usuarios con el área
            )

            session.add(nuevaArea)
            session.commit()
            session.refresh(nuevaArea)

            return jsonify({"mensaje": "Área creada correctamente", "idArea": nuevaArea.idArea}), 201

        except Exception as e:
            session.rollback()
            return responseError("ERROR_INTERNO", f"Ocurrió un error al crear el área: {str(e)}", 500)

        finally:
            session.close()
