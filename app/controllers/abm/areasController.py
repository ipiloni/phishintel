from flask import jsonify
from sqlalchemy import func
from app.backend.models import Usuario
from app.backend.models.usuarioxevento import UsuarioxEvento
from app.backend.models.resultadoEvento import ResultadoEvento
from app.backend.models.area import Area
from app.backend.models.error import responseError
from app.config.db_config import SessionLocal

class AreasController:

    @staticmethod
    def obtenerArea(idArea):
        session = SessionLocal()
        area = session.query(Area).filter_by(idArea=idArea).first()

        if area is None:
            return responseError("AREA_NO_ENCONTRADA", "El area no existe", 404)

        json = jsonify(area.get()), 200
        session.close()
        return json

    @staticmethod
    def obtenerTodasLasAreas():
        session = SessionLocal()
        areas = session.query(Area)
        session.close()
        areasARetornar = [area.get() for area in areas]
        return jsonify({"areas": areasARetornar}), 200

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

    @staticmethod
    def crearAreasBatch(payload):
        if not payload:
            return responseError("CAMPOS_OBLIGATORIOS", "Se requiere un cuerpo con 'areas'", 400)

        areas_data = payload if isinstance(payload, list) else payload.get("areas")
        if not isinstance(areas_data, list):
            return responseError("CAMPOS_OBLIGATORIOS", "'areas' debe ser una lista", 400)

        session = SessionLocal()
        resultados = []
        try:
            for idx, data in enumerate(areas_data):
                try:
                    if not data or "nombreArea" not in data or "usuarios" not in data:
                        resultados.append({"index": idx, "ok": False, "error": "Faltan campos obligatorios"})
                        continue

                    areaExistente = session.query(Area).filter_by(nombreArea=data["nombreArea"]).first()
                    if areaExistente is not None:
                        resultados.append({"index": idx, "ok": False, "error": f"Área ya existe id={areaExistente.idArea}"})
                        continue

                    usuarios_ids = data["usuarios"]
                    if not isinstance(usuarios_ids, list) or not all(isinstance(id, int) for id in usuarios_ids):
                        resultados.append({"index": idx, "ok": False, "error": "La lista de usuarios debe contener solo IDs numéricos"})
                        continue

                    usuarios = session.query(Usuario).filter(Usuario.idUsuario.in_(usuarios_ids)).all()
                    if len(usuarios) != len(set(usuarios_ids)):
                        resultados.append({"index": idx, "ok": False, "error": "Uno o más usuarios no existen"})
                        continue

                    nuevaArea = Area(
                        nombreArea=data["nombreArea"],
                        datosDelArea=data.get("datosArea"),
                        usuarios=usuarios
                    )
                    session.add(nuevaArea)
                    session.flush()
                    resultados.append({"index": idx, "ok": True, "idArea": nuevaArea.idArea})
                except Exception as e:
                    resultados.append({"index": idx, "ok": False, "error": str(e)})

            session.commit()
            ok_count = sum(1 for r in resultados if r.get("ok"))
            return jsonify({"creadas": ok_count, "resultados": resultados}), 201
        except Exception as e:
            session.rollback()
            return responseError("ERROR", f"No se pudo crear el batch de áreas: {str(e)}", 500)
        finally:
            session.close()

    @staticmethod
    def eliminarArea(idArea):
        session = SessionLocal()
        try:
            area = session.query(Area).filter_by(idArea=idArea).first()

            if not area:
                return responseError("AREA_NO_ENCONTRADA", "El area no existe", 404)

            # Desasignar usuarios de esta área
            for usuario in area.usuarios:
                usuario.area = None  # Esto setea idArea a NULL

            session.commit()

            # Ahora eliminar el área
            session.delete(area)
            session.commit()
            return jsonify({"mensaje": "Area eliminada correctamente"}), 200
        except Exception as e:
            session.rollback()
            return responseError("ERROR", f"No se pudo eliminar el area: {str(e)}", 500)
        finally:
            session.close()

    @staticmethod
    def editarArea(idArea, datos):
        session = SessionLocal()
        try:
            area = session.query(Area).filter_by(idArea=idArea).first()

            if not area:
                return responseError("AREA_NO_ENCONTRADA", "El área no existe", 404)

            # Actualizar solo si está presente en 'datos'
            if "nombreArea" in datos:
                area.nombreArea = datos["nombreArea"]

            if "datosDelArea" in datos:
                area.datosDelArea = datos["datosDelArea"]

            session.commit()

            return jsonify({"mensaje": "Área editada correctamente"}), 200

        except Exception as e:
            session.rollback()
            return responseError("ERROR", f"No se pudo editar el área: {str(e)}", 500)
        finally:
            session.close()

    @staticmethod
    def obtenerFallasPorArea():
        session = SessionLocal()
        try:
            # Traer todas las áreas para garantizar inclusión aunque no tengan fallas
            todas_las_areas = session.query(Area.idArea, Area.nombreArea).all()

            # Inicializar el diccionario con todas las áreas sin fallas
            areas_dict = {
                a.idArea: {
                    "idArea": a.idArea,
                    "nombreArea": a.nombreArea,
                    "totalFallas": 0,
                    "empleadosConFalla": 0,
                    "empleados": []
                }
                for a in todas_las_areas
            }

            # Query de fallas por usuario y área (solo cuenta FALLA)
            resultados = (
                session.query(
                    Area.idArea,
                    Area.nombreArea,
                    Usuario.idUsuario,
                    Usuario.nombre,
                    Usuario.apellido,
                    func.count(UsuarioxEvento.idEvento).label("cantidadFallas")
                )
                .join(Usuario, Usuario.idArea == Area.idArea)
                .join(UsuarioxEvento, UsuarioxEvento.idUsuario == Usuario.idUsuario)
                .filter(UsuarioxEvento.resultado == ResultadoEvento.FALLA)
                .group_by(
                    Area.idArea,
                    Area.nombreArea,
                    Usuario.idUsuario,
                    Usuario.nombre,
                    Usuario.apellido
                )
                .all()
            )

            # Completar métricas con los resultados
            for r in resultados:
                area_info = areas_dict.get(r.idArea)
                if not area_info:
                    # Por seguridad, aunque no debería pasar
                    areas_dict[r.idArea] = {
                        "idArea": r.idArea,
                        "nombreArea": r.nombreArea,
                        "totalFallas": 0,
                        "empleadosConFalla": 0,
                        "empleados": []
                    }
                    area_info = areas_dict[r.idArea]

                area_info["empleados"].append({
                    "idUsuario": r.idUsuario,
                    "nombre": r.nombre,
                    "apellido": r.apellido,
                    "cantidadFallas": int(r.cantidadFallas)
                })
                area_info["empleadosConFalla"] += 1
                area_info["totalFallas"] += int(r.cantidadFallas)

            return jsonify({"areas": list(areas_dict.values())}), 200
        except Exception as e:
            session.rollback()
            return responseError("ERROR", f"No se pudo obtener el resumen de fallas por área: {str(e)}", 500)
        finally:
            session.close()