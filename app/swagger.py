from flask import Blueprint, jsonify

swagger = Blueprint("swagger", __name__)


@swagger.route("/api/openapi.json", methods=["GET"])
def openapi_spec():
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "PhishIntel API",
            "version": "1.0.0",
            "description": "Documentación básica de endpoints de Usuarios"
        },
        "paths": {
            "/api/usuarios": {
                "get": {
                    "summary": "Obtener todos los usuarios",
                    "tags": ["Usuarios"],
                    "responses": {
                        "200": {
                            "description": "Lista de usuarios",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "usuarios": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/Usuario"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "summary": "Crear un usuario",
                    "tags": ["Usuarios"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/UsuarioCreate"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Usuario creado correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"mensaje": {"type": "string"}}
                                    }
                                }
                            }
                        },
                        "400": {"description": "Solicitud inválida", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/usuarios/{idUsuario}": {
                "put": {
                    "summary": "Editar un usuario",
                    "tags": ["Usuarios"],
                    "parameters": [
                        {"name": "idUsuario", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/UsuarioUpdate"}
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Usuario actualizado correctamente", "content": {"application/json": {"schema": {"type": "object", "properties": {"mensaje": {"type": "string"}}}}}},
                        "404": {"description": "Usuario no encontrado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                },
                "delete": {
                    "summary": "Eliminar un usuario",
                    "tags": ["Usuarios"],
                    "parameters": [
                        {"name": "idUsuario", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {
                        "200": {"description": "Usuario eliminado correctamente", "content": {"application/json": {"schema": {"type": "object", "properties": {"mensaje": {"type": "string"}}}}}},
                        "404": {"description": "Usuario no encontrado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Usuario": {
                    "type": "object",
                    "properties": {
                        "idUsuario": {"type": "integer"},
                        "nombreUsuario": {"type": "string"},
                        "nombre": {"type": "string"},
                        "apellido": {"type": "string"},
                        "correo": {"type": "string", "nullable": True},
                        "telefono": {"type": "string", "nullable": True},
                        "esAdministrador": {"type": "boolean", "nullable": True},
                        "idArea": {"type": "integer", "nullable": True}
                    }
                },
                "UsuarioCreate": {
                    "type": "object",
                    "required": ["nombreUsuario", "password", "nombre", "apellido"],
                    "properties": {
                        "nombreUsuario": {"type": "string"},
                        "password": {"type": "string"},
                        "nombre": {"type": "string"},
                        "apellido": {"type": "string"},
                        "telefono": {"type": "string"},
                        "correo": {"type": "string"},
                        "direccion": {"type": "string"},
                        "esAdministrador": {"type": "boolean"},
                        "idArea": {"type": "integer"}
                    }
                },
                "UsuarioUpdate": {
                    "type": "object",
                    "properties": {
                        "nombreUsuario": {"type": "string"},
                        "nombre": {"type": "string"},
                        "apellido": {"type": "string"},
                        "telefono": {"type": "string"},
                        "correo": {"type": "string"},
                        "direccion": {"type": "string"},
                        "esAdministrador": {"type": "boolean"},
                        "idArea": {"type": "integer"}
                    }
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "codigo": {"type": "string"},
                        "descripcion": {"type": "string"}
                    }
                }
            }
        }
    }
    return jsonify(spec)


@swagger.route("/apis/swagger", methods=["GET"])
def swagger_ui():
    html = """
<!DOCTYPE html>
<html lang=\"es\">
  <head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>PhishIntel Swagger</title>
    <link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist@5/swagger-ui.css\" />
    <style>body { margin: 0; padding: 0; } #swagger-ui { width: 100%; }</style>
  </head>
  <body>
    <div id=\"swagger-ui\"></div>
    <script src=\"https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js\"></script>
    <script>
      window.ui = SwaggerUIBundle({
        url: '/api/openapi.json',
        dom_id: '#swagger-ui',
        presets: [SwaggerUIBundle.presets.apis],
        layout: 'BaseLayout'
      });
    </script>
  </body>
</html>
"""
    return html


