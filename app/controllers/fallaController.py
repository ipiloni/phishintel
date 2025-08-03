#TODO

from flask import jsonify
from app.backend.models.error import responseError

# Variable global para contar fallas
conteo_fallas = {"total": 0}

class FallaController:

    @staticmethod
    def sumarFalla():
        try:
            conteo_fallas["total"] += 1
            return jsonify({"mensaje": "Falla registrada", "total": conteo_fallas["total"]}), 200
        except Exception as e:
            return responseError("ERROR", f"No se pudo registrar la falla: {str(e)}", 500)