from flask import jsonify


def responseError(codigo, descripcion, httpStatus):
    error_body = {
        "codigo": str(codigo),
        "descripcion": descripcion
    }
    return jsonify(error_body), httpStatus