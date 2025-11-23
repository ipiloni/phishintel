from flask import Blueprint, jsonify, send_file
import os

swagger = Blueprint("swagger", __name__)


@swagger.route("/api/openapi.json", methods=["GET"])
def openapi_spec():
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "PhishIntel API Privada",
            "version": "1.0.0",
            "description": "Documentación básica de endpoints"
        },
        "tags": [
            {"name": "👥 Usuarios", "description": "Gestión de usuarios"},
            {"name": "👤 Empleados", "description": "Funcionalidades específicas para empleados"},
            {"name": "🏢 Áreas", "description": "Gestión de áreas"},
            {"name": "📅 Eventos", "description": "Gestión de eventos"},
            {"name": "📊 Reportes", "description": "Reportes y métricas de fallas por área y empleado"},
            {"name": "📧 Emails", "description": "Envío de emails y notificaciones"},
            {"name": "💬 Mensajes", "description": "Envío de mensajes WhatsApp y SMS"},
            {"name": "📞 Llamadas", "description": "Gestión de llamadas y voces"},
            {"name": "🔐 Auth", "description": "Autenticación y gestión de sesiones"},
            {"name": "🤖 Telegram Bot", "description": "Gestión del bot de Telegram"},
            {"name": "📱 Telegram Account", "description": "Autenticación y envío de mensajes con cuenta propia de Telegram"},
            {"name": "🌐 Ngrok", "description": "Gestión de túneles ngrok temporales"},
            {"name": "⚠️ PELIGRO", "description": "Operaciones destructivas - USAR CON EXTREMA PRECAUCIÓN"}
        ],
        "paths": {
            "/api/usuarios": {
                "get": {
                    "summary": "Obtener todos los usuarios",
                    "tags": ["👥 Usuarios"],
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
                    "tags": ["👥 Usuarios"],
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
            "/api/usuarios/batch": {
                "post": {
                    "summary": "Crear múltiples usuarios",
                    "tags": ["👥 Usuarios"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "oneOf": [
                                        {"type": "array", "items": {"$ref": "#/components/schemas/UsuarioCreate"}},
                                        {"type": "object", "properties": {"usuarios": {"type": "array", "items": {"$ref": "#/components/schemas/UsuarioCreate"}}}}
                                    ]
                                },
                                "example": [
                                    {
                                        "nombreUsuario": "marcosgurruchaga",
                                        "password": "marcos.gurruchaga1",
                                        "nombre": "Marcos",
                                        "apellido": "Gurruchaga",
                                        "correo": "marcos.gurruchaga@pgcontrol.com.ar",
                                        "telefono": "+5491141635935",
                                        "idVoz": "GHUI7Bui6hqAYVXaCoEX"
                                    },
                                    {
                                        "nombreUsuario": "morarodriguez",
                                        "password": "mora.rodriguez1",
                                        "nombre": "Mora",
                                        "apellido": "Rodriguez",
                                        "correo": "mora.rodriguez@pgcontrol.com.ar",
                                        "telefono": "+5491165482219",
                                        "idVoz": "8DIlA8oISdnZSzlAFJq4"
                                    },
                                    {
                                        "nombreUsuario": "juanperez",
                                        "password": "juan.perez1",
                                        "nombre": "Juan",
                                        "apellido": "Perez",
                                        "correo": "juan.perez@pgcontrol.com.ar"
                                    },
                                    {
                                        "nombreUsuario": "pipiromagnoli",
                                        "password": "leandro.romagnoli1",
                                        "nombre": "Leandro",
                                        "apellido": "Romagnoli",
                                        "correo": "leandro.romagnoli@pgcontrol.com.ar"
                                    },
                                    {
                                        "nombreUsuario": "lauramartinez",
                                        "password": "laura.martinez1",
                                        "nombre": "Laura",
                                        "apellido": "Martinez",
                                        "correo": "laura.martinez@pgcontrol.com.ar"
                                    },
                                    {
                                        "nombreUsuario": "carloslopez",
                                        "password": "carlos.lopez1",
                                        "nombre": "Carlos",
                                        "apellido": "Lopez",
                                        "correo": "carlos.lopez@pgcontrol.com.ar"
                                    },
                                    {
                                        "nombreUsuario": "leonardopisculichi",
                                        "password": "leonardo.pisculichi1",
                                        "nombre": "Leonardo",
                                        "apellido": "Pisculichi",
                                        "correo": "leonardo.pisculichi@pgcontrol.com.ar"
                                    },
                                    {
                                        "nombreUsuario": "davidnalbandian",
                                        "password": "david.nalbandian1",
                                        "nombre": "David",
                                        "apellido": "Nalbandian",
                                        "correo": "david.nalbandian@pgcontrol.com.ar"
                                    },
                                    {
                                        "nombreUsuario": "delpo",
                                        "password": "juan.delpotro1",
                                        "nombre": "Juan Martin",
                                        "apellido": "Del Potro",
                                        "correo": "juan.delpotro@pgcontrol.com.ar"
                                    },
                                    {
                                        "nombreUsuario": "admin",
                                        "password": "adminadmin",
                                        "nombre": "Admin",
                                        "apellido": "de PhishIntel",
                                        "correo": "phishingintel@gmail.com",
                                        "esAdministrador": True
                                    }
                                ]
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "Resultado del batch"},
                        "400": {"description": "Solicitud inválida"}
                    }
                }
            },
            "/api/usuarios/{idUsuario}": {
                "get": {
                    "summary": "Obtener usuario por ID",
                    "tags": ["👥 Usuarios"],
                    "parameters": [
                        {"name": "idUsuario", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {
                        "200": {
                            "description": "Usuario encontrado",
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Usuario"}}}
                        },
                        "404": {"description": "Usuario no encontrado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                },
                "put": {
                    "summary": "Editar un usuario",
                    "tags": ["👥 Usuarios"],
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
                    "tags": ["👥 Usuarios"],
                    "parameters": [
                        {"name": "idUsuario", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {
                        "200": {"description": "Usuario eliminado correctamente", "content": {"application/json": {"schema": {"type": "object", "properties": {"mensaje": {"type": "string"}}}}}},
                        "404": {"description": "Usuario no encontrado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            }
            ,
            "/api/areas": {
                "get": {
                    "summary": "Obtener todas las áreas",
                    "tags": ["🏢 Áreas"],
                    "responses": {
                        "200": {
                            "description": "Lista de áreas",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "areas": {"type": "array", "items": {"$ref": "#/components/schemas/Area"}}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "summary": "Crear un área",
                    "tags": ["🏢 Áreas"],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AreaCreate"}}}
                    },
                    "responses": {"201": {"description": "Área creada"}, "400": {"description": "Solicitud inválida"}}
                }
            },
            "/api/areas/{idArea}": {
                "get": {
                    "summary": "Obtener área por ID",
                    "tags": ["🏢 Áreas"],
                    "parameters": [
                        {"name": "idArea", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {
                        "200": {"description": "Área encontrada", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Area"}}}},
                        "404": {"description": "Área no encontrada", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                },
                "put": {
                    "summary": "Editar un área",
                    "tags": ["🏢 Áreas"],
                    "parameters": [
                        {"name": "idArea", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AreaUpdate"}}}
                    },
                    "responses": {
                        "200": {"description": "Área editada", "content": {"application/json": {"schema": {"type": "object", "properties": {"mensaje": {"type": "string"}}}}}},
                        "404": {"description": "Área no encontrada", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                },
                "delete": {
                    "summary": "Eliminar un área",
                    "tags": ["🏢 Áreas"],
                    "parameters": [
                        {"name": "idArea", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {
                        "200": {"description": "Área eliminada", "content": {"application/json": {"schema": {"type": "object", "properties": {"mensaje": {"type": "string"}}}}}},
                        "404": {"description": "Área no encontrada", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/areas/batch": {
                "post": {
                    "summary": "Crear múltiples áreas",
                    "tags": ["🏢 Áreas"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "oneOf": [
                                        {"type": "array", "items": {"$ref": "#/components/schemas/AreaCreate"}},
                                        {"type": "object", "properties": {"areas": {"type": "array", "items": {"$ref": "#/components/schemas/AreaCreate"}}}}
                                    ]
                                },
                                "example": [
                                    {
                                        "nombreArea": "Ventas",
                                        "usuarios": [1, 2, 3]
                                    },
                                    {
                                        "nombreArea": "RRHH",
                                        "usuarios": [4, 5, 6]
                                    },
                                    {
                                        "nombreArea": "Compras",
                                        "usuarios": [7, 8, 9]
                                    }
                                ]
                            }
                        }
                    },
                    "responses": {"201": {"description": "Resultado del batch"}, "400": {"description": "Solicitud inválida"}}
                }
            }
            ,
            "/api/areas/fallas": {
                "get": {
                    "summary": "Obtener fallas por área",
                    "description": "Obtiene un listado de todas las áreas con métricas de fallas agregadas por empleados. Permite filtrar por tipos de evento específicos.",
                    "tags": ["📊 Reportes"],
                    "parameters": [
                        {
                            "name": "tipo_evento",
                            "in": "query",
                            "description": "Filtrar por tipos de evento (puede especificar múltiples valores)",
                            "required": False,
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["CORREO", "MENSAJE", "LLAMADA"]
                                }
                            },
                            "style": "form",
                            "explode": True
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Listado de áreas con métricas de fallas",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "areas": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/AreaFallas"}
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "500": {"description": "Error del servidor", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/areas/fallas-fecha": {
                "get": {
                    "summary": "Obtener fallas por área y fecha",
                    "description": "Obtiene métricas de fallas por área agrupadas por períodos de tiempo. Permite filtrar por tipos de evento y períodos específicos.",
                    "tags": ["📊 Reportes"],
                    "parameters": [
                        {
                            "name": "tipo_evento",
                            "in": "query",
                            "description": "Filtrar por tipos de evento (puede especificar múltiples valores)",
                            "required": False,
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["CORREO", "MENSAJE", "LLAMADA"]
                                }
                            },
                            "style": "form",
                            "explode": True
                        },
                        {
                            "name": "periodo",
                            "in": "query",
                            "description": "Filtrar por períodos de tiempo (puede especificar múltiples valores)",
                            "required": False,
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "style": "form",
                            "explode": True
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Métricas de fallas por área y fecha",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "areas": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/AreaFallas"}
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "500": {"description": "Error del servidor", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/areas/fallas-campania": {
                "get": {
                    "summary": "Obtener fallas por área y campaña",
                    "description": "Obtiene métricas de fallas por área agrupadas por campañas específicas. Permite filtrar por áreas particulares.",
                    "tags": ["📊 Reportes"],
                    "parameters": [
                        {
                            "name": "area",
                            "in": "query",
                            "description": "Filtrar por áreas específicas (puede especificar múltiples valores)",
                            "required": False,
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "style": "form",
                            "explode": True
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Métricas de fallas por área y campaña",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "areas": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/AreaFallas"}
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "500": {"description": "Error del servidor", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/areas/fallas-empleados": {
                "get": {
                    "summary": "Obtener fallas por empleado",
                    "description": "Obtiene un listado de todos los empleados con métricas de fallas individuales. Permite filtrar por tipos de evento específicos y áreas.",
                    "tags": ["📊 Reportes"],
                    "parameters": [
                        {
                            "name": "tipo_evento",
                            "in": "query",
                            "description": "Filtrar por tipos de evento (puede especificar múltiples valores)",
                            "required": False,
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["CORREO", "MENSAJE", "LLAMADA"]
                                }
                            },
                            "style": "form",
                            "explode": True
                        },
                        {
                            "name": "area",
                            "in": "query",
                            "description": "Filtrar por áreas específicas (puede especificar múltiples valores)",
                            "required": False,
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "style": "form",
                            "explode": True
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Listado de empleados con métricas de fallas",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "empleados": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/EmpleadoFalla"}
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "500": {"description": "Error del servidor", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/areas/fallas-empleados-scoring": {
                "get": {
                    "summary": "🎯 Obtener Fallas por Empleado con Sistema de Scoring Invertido",
                    "description": "Obtiene un listado completo de todos los empleados con sistema de scoring invertido (100-0 puntos) y niveles de riesgo. Incluye empleados sin fallas. Los empleados empiezan con 100 puntos y van perdiendo por fallas: Falla simple = -5 pts, Falla grave = -10 pts (independiente del tipo de evento). Penalización adicional por haber fallado en el pasado basada en el tipo de falla. Pueden recuperar puntos reportando eventos: +5 pts por evento reportado. Clasifica en niveles de riesgo: Sin riesgo (100), Bajo (90-99), Medio (75-89), Alto (50-74), Máximo (0-49). El área muestra promedio de puntos de empleados. Implementado en ResultadoEventoController.",
                    "tags": ["📊 Reportes"],
                    "parameters": [
                        {
                            "name": "tipo_evento",
                            "in": "query",
                            "description": "Filtrar por tipos de evento (puede especificar múltiples valores)",
                            "required": False,
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["CORREO", "MENSAJE", "LLAMADA"]
                                }
                            },
                            "style": "form",
                            "explode": True
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Listado de áreas con empleados y sistema de scoring",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "areas": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "idArea": {"type": "integer"},
                                                        "nombreArea": {"type": "string"},
                                                        "promedio_puntos": {"type": "number", "format": "float", "description": "Promedio de puntos restantes de empleados del área"},
                                                        "total_fallas": {"type": "integer", "description": "Total de fallas del área"},
                                                        "total_reportados": {"type": "integer", "description": "Total de eventos reportados del área"},
                                                        "total_eventos": {"type": "integer", "description": "Total de eventos del área"},
                                                        "empleados_con_fallas": {"type": "integer", "description": "Número de empleados con fallas"},
                                                        "empleados": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "idUsuario": {"type": "integer"},
                                                                    "nombre": {"type": "string"},
                                                                    "apellido": {"type": "string"},
                                                                    "puntos_restantes": {"type": "integer", "description": "Puntos restantes del empleado (100 - puntos perdidos - penalizacion_falla_pasado + puntos ganados)"},
                                                                    "puntos_perdidos": {"type": "integer", "description": "Puntos perdidos por fallas del empleado (5 pts por falla simple, 10 pts por falla grave)"},
                                                                    "puntos_ganados": {"type": "integer", "description": "Puntos ganados por eventos reportados (5 pts por reporte)"},
                                                                    "penalizacion_falla_pasado": {"type": "integer", "description": "Penalización por haber fallado en el pasado (basada en tipo de falla: 5 pts por simple, 10 pts por grave)"},
                                                                    "ha_fallado_en_pasado": {"type": "boolean", "description": "Indica si el empleado ha fallado en el pasado en algún evento"},
                                                                    "total_fallas": {"type": "integer", "description": "Total de fallas del empleado"},
                                                                    "total_reportados": {"type": "integer", "description": "Total de eventos reportados del empleado"},
                                                                    "total_eventos": {"type": "integer", "description": "Total de eventos del empleado"},
                                                                    "nivel_riesgo": {"type": "string", "enum": ["Sin riesgo", "Riesgo bajo", "Riesgo medio", "Riesgo alto", "Riesgo máximo"], "description": "Nivel de riesgo basado en puntos"},
                                                                    "fallas_por_tipo": {
                                                                        "type": "object",
                                                                        "description": "Desglose de fallas por tipo de falla (simples/graves)",
                                                                        "properties": {
                                                                            "fallas_simples": {"type": "integer", "description": "Cantidad de fallas simples"},
                                                                            "fallas_graves": {"type": "integer", "description": "Cantidad de fallas graves"}
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "500": {"description": "Error del servidor", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/scoring/empleado/{idUsuario}": {
                "get": {
                    "summary": "🎯 Obtener Scoring Individual de Empleado (Sistema Invertido)",
                    "description": "Calcula el scoring individual de un empleado específico con sistema invertido (100-0 puntos). El empleado empieza con 100 puntos y va perdiendo por fallas: Falla simple = -5 pts, Falla grave = -10 pts (independiente del tipo de evento). Penalización adicional por haber fallado en el pasado basada en el tipo de falla. Puede recuperar puntos reportando eventos: +5 pts por evento reportado. Clasifica en niveles de riesgo: Sin riesgo (100), Bajo (90-99), Medio (75-89), Alto (50-74), Máximo (0-49). Incluye puntos restantes, puntos perdidos, puntos ganados, penalización por falla en el pasado y desglose detallado por tipo de falla (simples/graves). Implementado en ResultadoEventoController.",
                    "tags": ["📊 Reportes"],
                    "parameters": [
                        {
                            "name": "idUsuario",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                            "description": "ID del usuario para calcular scoring"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Scoring del empleado calculado exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "idUsuario": {"type": "integer"},
                                            "nombre": {"type": "string"},
                                            "apellido": {"type": "string"},
                                            "puntos_restantes": {"type": "integer", "description": "Puntos restantes del empleado (100 - puntos perdidos - penalizacion_falla_pasado + puntos ganados)"},
                                            "puntos_perdidos": {"type": "integer", "description": "Puntos perdidos por fallas (5 pts por falla simple, 10 pts por falla grave)"},
                                            "puntos_ganados": {"type": "integer", "description": "Puntos ganados por eventos reportados (5 pts por reporte)"},
                                            "penalizacion_falla_pasado": {"type": "integer", "description": "Penalización por haber fallado en el pasado (basada en tipo de falla: 5 pts por simple, 10 pts por grave)"},
                                            "ha_fallado_en_pasado": {"type": "boolean", "description": "Indica si el empleado ha fallado en el pasado en algún evento"},
                                            "puntaje_inicial": {"type": "integer", "description": "Puntaje inicial (100 puntos)"},
                                            "total_fallas": {"type": "integer", "description": "Total de fallas"},
                                            "total_reportados": {"type": "integer", "description": "Total de eventos reportados"},
                                            "nivel_riesgo": {"type": "string", "enum": ["Sin riesgo", "Riesgo bajo", "Riesgo medio", "Riesgo alto", "Riesgo máximo"]},
                                            "desglose_por_tipo": {
                                                "type": "object",
                                                "description": "Desglose detallado por tipo de falla",
                                                "properties": {
                                                    "fallas_simples": {
                                                        "type": "object",
                                                        "properties": {
                                                            "cantidad": {"type": "integer"},
                                                            "puntos_perdidos": {"type": "integer", "description": "Cantidad × 5 puntos perdidos"}
                                                        }
                                                    },
                                                    "fallas_graves": {
                                                        "type": "object",
                                                        "properties": {
                                                            "cantidad": {"type": "integer"},
                                                            "puntos_perdidos": {"type": "integer", "description": "Cantidad × 10 puntos perdidos"}
                                                        }
                                                    }
                                                }
                                            },
                                            "eventos_detalle": {
                                                "type": "object",
                                                "description": "Detalle de eventos con información de esFallaGrave",
                                                "properties": {
                                                    "activos": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "idEvento": {"type": "integer"},
                                                                "titulo": {"type": "string"},
                                                                "tipoEvento": {"type": "string"},
                                                                "fechaCreacion": {"type": "string", "format": "date-time"},
                                                                "puntos": {"type": "integer", "description": "5 para falla simple, 10 para falla grave"},
                                                                "esFallaGrave": {"type": "boolean"}
                                                            }
                                                        }
                                                    },
                                                    "reportados": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "idEvento": {"type": "integer"},
                                                                "titulo": {"type": "string"},
                                                                "tipoEvento": {"type": "string"},
                                                                "fechaCreacion": {"type": "string", "format": "date-time"},
                                                                "puntos": {"type": "integer", "description": "5 puntos por reporte"},
                                                                "haFalladoEnElPasado": {"type": "boolean"},
                                                                "puntosFallaPasada": {"type": "integer", "description": "5 para falla simple pasada, 10 para falla grave pasada"},
                                                                "esFallaGrave": {"type": "boolean"}
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "404": {"description": "Usuario no encontrado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "500": {"description": "Error del servidor", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/kpis/tiempo-respuesta": {
                "get": {
                    "summary": "📊 Obtener KPI de Tiempo de Respuesta Promedio",
                    "description": "Calcula el tiempo de respuesta promedio para eventos reportados por usuarios. Mide la diferencia en horas entre la fecha de reporte (usuarioxevento.fechaReporte) y la fecha de creación del evento (evento.fechaEvento). Incluye clasificación automática basada en objetivos de madurez organizacional. Implementado en ControllerKpis.",
                    "tags": ["📊 Reportes"],
                    "responses": {
                        "200": {
                            "description": "KPI de tiempo de respuesta calculado exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "tiempoRespuestaPromedio": {
                                                "type": "number",
                                                "format": "float",
                                                "description": "Tiempo promedio de respuesta en horas",
                                                "example": 2.5
                                            },
                                            "tiempoRespuestaMediana": {
                                                "type": "number",
                                                "format": "float",
                                                "description": "Mediana del tiempo de respuesta en horas",
                                                "example": 1.8
                                            },
                                            "tiempoRespuestaP90": {
                                                "type": "number",
                                                "format": "float",
                                                "description": "Percentil 90 del tiempo de respuesta en horas",
                                                "example": 8.5
                                            },
                                            "totalEventosReportados": {
                                                "type": "integer",
                                                "description": "Número total de eventos reportados analizados",
                                                "example": 45
                                            },
                                            "clasificacion": {
                                                "type": "string",
                                                "description": "Clasificación de madurez organizacional basada en los tiempos de respuesta",
                                                "enum": [
                                                    "Vigilantes del Ciberespacio",
                                                    "Guardianes Anti-Phishing", 
                                                    "Defensores Digitales",
                                                    "Aprendices de Seguridad",
                                                    "Presas del Phishing",
                                                    "Crítico",
                                                    "Sin datos"
                                                ],
                                                "example": "Defensores Digitales"
                                            },
                                            "nivel": {
                                                "type": "integer",
                                                "description": "Nivel de madurez (0-5, donde 5 es el más alto)",
                                                "minimum": 0,
                                                "maximum": 5,
                                                "example": 3
                                            },
                                            "descripcion": {
                                                "type": "string",
                                                "description": "Descripción detallada de la clasificación y criterios utilizados",
                                                "example": "Respuesta estándar con procesos establecidos. Mediana ≤ 4h, P90 ≤ 48h"
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "500": {
                            "description": "Error del servidor al calcular el KPI",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/kpis/tasa-fallas": {
                "get": {
                    "summary": "⚠️ Obtener KPI de Tasa de Fallas",
                    "description": "Calcula la tasa de fallas basada en los intentos de phishing (usuarios asignados a eventos). Cada usuario asignado a un evento representa un intento de phishing individual. Calcula el porcentaje de intentos que resultaron en FALLA. Incluye clasificación automática en 5 niveles de madurez organizacional. Implementado en ControllerKpis.",
                    "tags": ["📊 Reportes"],
                    "responses": {
                        "200": {
                            "description": "KPI de tasa de fallas calculado exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "tasaFallas": {
                                                "type": "number",
                                                "format": "float",
                                                "description": "Porcentaje de intentos de phishing que resultaron en FALLA",
                                                "example": 15.5
                                            },
                                            "totalIntentos": {
                                                "type": "integer",
                                                "description": "Número total de intentos de phishing (usuarios asignados a eventos)",
                                                "example": 120
                                            },
                                            "intentosConFalla": {
                                                "type": "integer",
                                                "description": "Número de intentos que resultaron en FALLA",
                                                "example": 18
                                            },
                                            "intentosSinFalla": {
                                                "type": "integer",
                                                "description": "Número de intentos que NO resultaron en FALLA",
                                                "example": 102
                                            },
                                            "clasificacion": {
                                                "type": "string",
                                                "description": "Clasificación de madurez organizacional basada en la tasa de fallas",
                                                "enum": [
                                                    "Vigilantes del Ciberespacio",
                                                    "Guardianes Anti-Phishing",
                                                    "Defensores Digitales",
                                                    "Aprendices de Seguridad",
                                                    "Presas del Phishing",
                                                    "Datos Insuficientes"
                                                ],
                                                "example": "Aprendices de Seguridad"
                                            },
                                            "nivel": {
                                                "type": "integer",
                                                "description": "Nivel de madurez (0-5, donde 5 es el más alto). Nivel 0 indica datos insuficientes",
                                                "minimum": 0,
                                                "maximum": 5,
                                                "example": 2
                                            },
                                            "descripcion": {
                                                "type": "string",
                                                "description": "Descripción detallada de la clasificación y criterios utilizados",
                                                "example": "Fallas frecuentes, requieren refuerzo de procesos y controles. Failure Rate > 10% y ≤ 20%"
                                            },
                                            "insuficienteDatos": {
                                                "type": "boolean",
                                                "description": "Indica si hay suficientes datos para mostrar el KPI (mínimo 5 intentos de phishing)",
                                                "example": False
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "500": {
                            "description": "Error del servidor al calcular el KPI",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/kpis/promedio-scoring": {
                "get": {
                    "summary": "🎯 Obtener KPI de Promedio de Scoring",
                    "description": "Calcula el promedio de scoring de todos los empleados de la empresa utilizando el sistema de scoring invertido (100-0 puntos). Incluye estadísticas completas: promedio, mediana, percentil 10, y clasificación automática en 5 niveles de madurez organizacional. Requiere mínimo 5 intentos de phishing para mostrar resultados. Implementado en KpiController.",
                    "tags": ["📊 Reportes"],
                    "responses": {
                        "200": {
                            "description": "KPI de promedio de scoring calculado exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "promedioScoring": {
                                                "type": "number",
                                                "format": "float",
                                                "description": "Promedio de scoring de todos los empleados (sistema 100-0 puntos)",
                                                "example": 85.5
                                            },
                                            "medianaScoring": {
                                                "type": "number",
                                                "format": "float",
                                                "description": "Mediana de scoring de todos los empleados",
                                                "example": 87.0
                                            },
                                            "percentil10Scoring": {
                                                "type": "number",
                                                "format": "float",
                                                "description": "Percentil 10 del scoring (peores 10% de empleados)",
                                                "example": 65.0
                                            },
                                            "totalIntentosPhishing": {
                                                "type": "integer",
                                                "description": "Número total de intentos de phishing en la empresa",
                                                "example": 150
                                            },
                                            "clasificacion": {
                                                "type": "string",
                                                "description": "Clasificación de madurez organizacional basada en el promedio de scoring",
                                                "enum": [
                                                    "Vigilantes del Ciberespacio",
                                                    "Guardianes Anti-Phishing",
                                                    "Defensores Digitales",
                                                    "Aprendices de Ciberseguridad",
                                                    "Presas del Phishing",
                                                    "Datos Insuficientes",
                                                    "Sin datos"
                                                ],
                                                "example": "Defensores Digitales"
                                            },
                                            "nivel": {
                                                "type": "integer",
                                                "description": "Nivel de madurez (0-5, donde 5 es el más alto). Nivel 0 indica datos insuficientes",
                                                "minimum": 0,
                                                "maximum": 5,
                                                "example": 3
                                            },
                                            "descripcion": {
                                                "type": "string",
                                                "description": "Descripción detallada de la clasificación y criterios utilizados",
                                                "example": "Rendimiento estándar en ciberseguridad. Promedio entre 90-100 puntos"
                                            },
                                            "insuficienteDatos": {
                                                "type": "boolean",
                                                "description": "Indica si hay suficientes datos para mostrar el KPI (mínimo 5 intentos de phishing)",
                                                "example": False
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "500": {
                            "description": "Error del servidor al calcular el KPI",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/eventos": {
                "get": {
                    "summary": "Obtener todos los eventos",
                    "tags": ["📅 Eventos"],
                    "responses": {
                        "200": {
                            "description": "Lista de eventos",
                            "content": {"application/json": {"schema": {"type": "object", "properties": {"eventos": {"type": "array", "items": {"$ref": "#/components/schemas/Evento"}}}}}}
                        }
                    }
                },
                "post": {
                    "summary": "Crear un evento",
                    "tags": ["📅 Eventos"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/EventoCreate"},
                                "example": {
                                    "tipoEvento": "CORREO",
                                    "fechaEvento": "2025-08-11T10:30:00",
                                    "registroEvento": {
                                        "asunto": "Prueba de asunto del evento",
                                        "cuerpo": "<p>Este es el cuerpo del evento en HTML o texto</p>"
                                    }
                                }
                            }
                        }
                    },
                    "responses": {"201": {"description": "Evento creado"}, "400": {"description": "Solicitud inválida"}}
                }
            },
            "/api/eventos/{idEvento}": {
                "get": {
                    "summary": "Obtener evento por ID",
                    "tags": ["📅 Eventos"],
                    "parameters": [{"name": "idEvento", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {"200": {"description": "Evento", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Evento"}}}}, "404": {"description": "No encontrado"}}
                },
                "put": {
                    "summary": "Editar un evento",
                    "tags": ["📅 Eventos"],
                    "parameters": [{"name": "idEvento", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/EventoUpdate"}}}},
                    "responses": {"200": {"description": "Evento editado"}, "404": {"description": "No encontrado"}}
                },
                "delete": {
                    "summary": "Eliminar un evento",
                    "tags": ["📅 Eventos"],
                    "parameters": [{"name": "idEvento", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {"200": {"description": "Evento eliminado"}, "404": {"description": "No encontrado"}}
                }
            },
            "/api/eventos/{idEvento}/usuarios/{idUsuario}": {
                "post": {
                    "summary": "Asociar usuario a evento con resultado y fechas",
                    "tags": ["📅 Eventos"],
                    "parameters": [
                        {"name": "idEvento", "in": "path", "required": True, "schema": {"type": "integer"}},
                        {"name": "idUsuario", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AsociarUsuarioEvento"},
                                "examples": {
                                    "01_solo_resultado": {
                                        "summary": "Solo resultado (sin fechas)",
                                        "value": {
                                            "resultado": "PENDIENTE"
                                        }
                                    },
                                    "02_con_fechas": {
                                        "summary": "Con fechas específicas",
                                        "value": {
                                            "resultado": "FALLA",
                                            "fechaFalla": "2025-01-15T10:30:00",
                                            "fechaReporte": "2025-01-15T11:00:00"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Usuario asociado correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {"description": "Solicitud inválida - Faltan parámetros o fechas inválidas"},
                        "404": {"description": "Evento o usuario no encontrado"}
                    }
                }
            },
            "/api/sumar-falla": {
                "post": {
                    "summary": "Marcar evento como falla simple (resta 5 puntos, usa fecha actual por defecto)",
                    "description": "Registra una falla simple para un usuario en un evento. Las fallas simples restan 5 puntos del scoring del empleado, independientemente del tipo de evento (correo, mensaje, llamada).",
                    "tags": ["📅 Eventos"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SumarFalla"},
                                "examples": {
                                    "01_sin_fecha": {
                                        "summary": "Sin fecha (usa fecha actual)",
                                        "value": {
                                            "idUsuario": 1,
                                            "idEvento": 1
                                        }
                                    },
                                    "02_con_fecha": {
                                        "summary": "Con fecha específica",
                                        "value": {
                                            "idUsuario": 1,
                                            "idEvento": 1,
                                            "fechaFalla": "2025-01-15T10:30:00"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Falla simple registrada correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {"type": "string"},
                                            "idUsuario": {"type": "integer"},
                                            "idEvento": {"type": "integer"},
                                            "fechaFalla": {"type": "string", "format": "date-time"},
                                            "esFallaGrave": {"type": "boolean", "description": "Indica si es falla grave (siempre false para este endpoint)"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {"description": "Solicitud inválida - Faltan parámetros o fecha inválida"},
                        "404": {"description": "No existe relación entre el usuario y el evento"}
                    }
                }
            },
            "/api/sumar-falla-grave": {
                "post": {
                    "summary": "Marcar evento como falla grave (resta 10 puntos, usa fecha actual por defecto)",
                    "description": "Registra una falla grave para un usuario en un evento. Las fallas graves restan 10 puntos del scoring del empleado, independientemente del tipo de evento (correo, mensaje, llamada). Se registra cuando el usuario ingresa credenciales en formularios de phishing.",
                    "tags": ["📅 Eventos"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SumarFallaGrave"},
                                "examples": {
                                    "01_sin_fecha": {
                                        "summary": "Sin fecha (usa fecha actual)",
                                        "value": {
                                            "idUsuario": 1,
                                            "idEvento": 1
                                        }
                                    },
                                    "02_con_fecha": {
                                        "summary": "Con fecha específica",
                                        "value": {
                                            "idUsuario": 1,
                                            "idEvento": 1,
                                            "fechaFalla": "2025-01-15T10:30:00"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Falla grave registrada correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {"type": "string"},
                                            "idUsuario": {"type": "integer"},
                                            "idEvento": {"type": "integer"},
                                            "fechaFalla": {"type": "string", "format": "date-time"},
                                            "esFallaGrave": {"type": "boolean", "description": "Indica si es falla grave (siempre true para este endpoint)"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {"description": "Solicitud inválida - Faltan parámetros o fecha inválida"},
                        "404": {"description": "No existe relación entre el usuario y el evento"},
                        "500": {"description": "Error del servidor"}
                    }
                }
            },
            "/api/sumar-reportado": {
                "post": {
                    "summary": "Marcar evento como reportado (usa fecha actual por defecto)",
                    "tags": ["📅 Eventos"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SumarReportado"},
                                "examples": {
                                    "01_sin_fecha": {
                                        "summary": "Sin fecha (usa fecha actual)",
                                        "value": {
                                            "idUsuario": 1,
                                            "idEvento": 1
                                        }
                                    },
                                    "02_con_fecha": {
                                        "summary": "Con fecha específica",
                                        "value": {
                                            "idUsuario": 1,
                                            "idEvento": 1,
                                            "fechaReporte": "2025-01-15T10:30:00"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Reporte registrado correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {"type": "string"},
                                            "idUsuario": {"type": "integer"},
                                            "idEvento": {"type": "integer"},
                                            "fechaReporte": {"type": "string", "format": "date-time"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {"description": "Solicitud inválida - Faltan parámetros o fecha inválida"},
                        "404": {"description": "No existe relación entre el usuario y el evento"}
                    }
                }
            },
            "/api/email/enviar-id": {
                "post": {
                    "summary": "Enviar email por ID de usuario con nivel de dificultad",
                    "description": "Envía un email de phishing a un usuario específico. El nivel de dificultad determina el proveedor de envío: Fácil/Medio usa PhishIntel, Difícil usa PGControl. Para dificultad Difícil, se requiere especificar el remitente (idUsuarioRemitente).",
                    "tags": ["📧 Emails"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/EmailEnviarID"},
                                "examples": {
                                    "facil": {
                                        "summary": "Dificultad Fácil",
                                        "description": "Email de dificultad fácil desde phishingintel@gmail.com",
                                        "value": {
                                            "proveedor": "twilio",
                                            "idUsuarioDestinatario": 1,
                                            "asunto": "Mensaje de dificultad fácil - Verificación de cuenta",
                                            "cuerpo": "<p>Este es un mensaje de prueba de dificultad fácil</p>",
                                            "dificultad": "Fácil"
                                        }
                                    },
                                    "medio": {
                                        "summary": "Dificultad Medio",
                                        "description": "Email de dificultad medio desde administracion@pgcontrol.lat",
                                        "value": {
                                            "proveedor": "twilio",
                                            "idUsuarioDestinatario": 2,
                                            "asunto": "Mensaje de dificultad medio - Actualización de seguridad",
                                            "cuerpo": "<p>Este es un mensaje de prueba de dificultad medio</p>",
                                            "dificultad": "Medio"
                                        }
                                    },
                                    "dificil": {
                                        "summary": "Dificultad Difícil",
                                        "description": "Email de dificultad difícil con remitente configurable",
                                        "value": {
                                            "proveedor": "twilio",
                                            "idUsuarioDestinatario": 3,
                                            "idUsuarioRemitente": 4,
                                            "asunto": "Mensaje de dificultad difícil - Revisión urgente de documentos",
                                            "cuerpo": "<p>Este es un mensaje de prueba de dificultad difícil</p>",
                                            "dificultad": "Difícil"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "Email enviado correctamente"},
                        "400": {"description": "Solicitud inválida"},
                        "404": {"description": "Usuario no encontrado"}
                    }
                }
            },
            "/api/email/generar": {
                "post": {
                    "summary": "Generar email con IA (solo generar, no enviar)",
                    "tags": ["📧 Emails"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/EmailGenerar"},
                                "example": {
                                    "contexto": "Armame un email del estilo Phishing avisando que hay una compra no reconocida",
                                    "formato": "HTML",
                                    "nivel": "2"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Email generado correctamente"},
                        "400": {"description": "Solicitud inválida"}
                    }
                }
            },
            "/api/email/notificar": {
                "post": {
                    "summary": "Enviar notificación desde PhishIntel",
                    "tags": ["📧 Emails"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/EmailNotificar"},
                                "example": {
                                    "destinatario": "phishingintel@gmail.com",
                                    "asunto": "Notificación de seguridad",
                                    "cuerpo": "<p>Se ha detectado una actividad sospechosa en su cuenta</p>"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "Notificación enviada correctamente"},
                        "400": {"description": "Solicitud inválida"}
                    }
                }
            },
            "/api/mensajes/whatsapp-twilio": {
                "post": {
                    "summary": "⚠️ SOLO NRO IGNA - Enviar mensaje por WhatsApp (Twilio)",
                    "description": "⚠️ Este endpoint tiene limitaciones y solo funciona con números específicos",
                    "tags": ["💬 Mensajes"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/MensajeWhatsApp"},
                                "example": {
                                    "remitente": "+14155238886",
                                    "destinatario": "+5493775639378",
                                    "mensaje": "Esta es una prueba desde Phishintel API localhost:8080"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "Mensaje WhatsApp enviado correctamente"},
                        "400": {"description": "Solicitud inválida"},
                        "500": {"description": "Error en el servicio"}
                    }
                }
            },
            "/api/mensajes/sms": {
                "post": {
                    "summary": "⚠️ SOLO NRO IGNA - Enviar mensaje por SMS (Twilio)",
                    "tags": ["💬 Mensajes"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/MensajeSMS"},
                                "example": {
                                    "remitente": "+19528009780",
                                    "destinatario": "+543775639378",
                                    "mensaje": "Esta es una prueba desde Phishintel API localhost:8080"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "Mensaje SMS enviado correctamente"},
                        "400": {"description": "Solicitud inválida"},
                        "500": {"description": "Error en el servicio"}
                    }
                }
            },
            "/api/mensajes/whatsapp-selenium": {
                "post": {
                    "summary": "❌ NO FUNCIONA - Enviar mensaje por WhatsApp usando Selenium",
                    "description": "❌ Este endpoint no funciona correctamente actualmente. Envía un mensaje de WhatsApp usando Selenium WebDriver. Requiere que el usuario esté previamente logueado en WhatsApp Web en Chrome Profile 14.",
                    "tags": ["💬 Mensajes"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/MensajeWhatsAppSelenium"},
                                "example": {
                                    "destinatario": "Marcos Gurruchaga",
                                    "mensaje": "Hola, esto es un mensaje desde Python"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Mensaje WhatsApp enviado correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {"type": "string"},
                                            "destinatario": {"type": "string"},
                                            "contenido": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {"description": "Solicitud inválida - Faltan campos obligatorios"},
                        "404": {"description": "Contacto no encontrado, perfil Profile 14 no existe o ChromeDriver no encontrado"},
                        "408": {"description": "Timeout - Asegúrate de estar logueado en Profile 14 de WhatsApp Web"},
                        "409": {"description": "Directorio de datos de Chrome en uso - Cierra Chrome y vuelve a intentar"},
                        "500": {"description": "Error en el servicio, perfil de Chrome, campo de mensaje, botón de enviar no encontrado o elemento obsoleto"}
                    }
                }
            },
            "/api/mensajes/whatsapp-whapi": {
                "post": {
                    "summary": "✅ FUNCIONA - Enviar mensaje por WhatsApp usando whapi.cloud",
                    "description": "Envía un mensaje de WhatsApp usando la API de whapi.cloud. Si no se especifica destinatario, se envía al número por defecto +54 9 11 4163-5935. El sistema formatea automáticamente los números argentinos al formato requerido (549XXXXXXXXX).",
                    "tags": ["💬 Mensajes"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/MensajeWhapiCloud"},
                                "example": {
                                    "mensaje": "Hola, esto es un mensaje desde PhishIntel via whapi.cloud",
                                    "destinatario": "+54 9 11 4163-5935"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Mensaje WhatsApp enviado correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {"type": "string"},
                                            "destinatario": {"type": "string"},
                                            "destinatario_formateado": {"type": "string"},
                                            "contenido": {"type": "string"},
                                            "id": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {"description": "Solicitud inválida - Falta el campo obligatorio 'mensaje' o número inválido"},
                        "500": {"description": "Token no configurado o error en el servicio"},
                        "503": {"description": "Error de conexión con whapi.cloud"},
                        "408": {"description": "Timeout al enviar mensaje"}
                    }
                }
            },
            "/api/mensajes/whatsapp-grupo-whapi": {
                "post": {
                    "summary": "✅ FUNCIONA - Enviar mensaje a grupo de WhatsApp usando whapi.cloud",
                    "description": "Envía un mensaje de WhatsApp a un grupo usando la API de whapi.cloud. Si no se especifica grupo_id, se envía al grupo por defecto 'Proyecto Grupo 8 🤝🏻✨🎉🙌🏻'. El grupo_id debe ser el identificador único del grupo de WhatsApp.",
                    "tags": ["💬 Mensajes"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/MensajeWhapiGrupo"},
                                "example": {
                                    "mensaje": "Hola grupo! Este es un mensaje desde PhishIntel via whapi.cloud",
                                    "grupo_id": "120363416003158863@g.us"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Mensaje WhatsApp enviado correctamente al grupo",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {"type": "string"},
                                            "grupo_id": {"type": "string"},
                                            "contenido": {"type": "string"},
                                            "id": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {"description": "Solicitud inválida - Falta el campo obligatorio 'mensaje'"},
                        "500": {"description": "Token no configurado o error en el servicio"},
                        "503": {"description": "Error de conexión con whapi.cloud"},
                        "408": {"description": "Timeout al enviar mensaje al grupo"}
                    }
                }
            },
            "/api/mensaje/generar": {
                "post": {
                    "summary": "🤖 Generar mensaje de phishing con IA (solo generar, no enviar)",
                    "description": "Genera un mensaje de phishing personalizado usando Gemini AI. El mensaje se genera como texto plano para WhatsApp/SMS, adaptado al nivel de dificultad especificado.",
                    "tags": ["💬 Mensajes"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/MensajeGenerar"},
                                "example": {
                                    "contexto": "Área: Ventas, Usuario: Juan Pérez, La fecha que sea el 24/8/2025, Sin links, No le pidas informacion ni pongas un asunto en mayuscula. Pone un tono mas corporativo para que no llegue a spam.",
                                    "nivel": "Medio"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Mensaje generado correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {"type": "string", "description": "Contenido del mensaje generado por IA"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {"description": "Solicitud inválida - Falta el campo obligatorio 'contexto'"},
                        "500": {"description": "Error en la API de Gemini"}
                    }
                }
            },
            "/api/mensaje/enviar-id": {
                "post": {
                    "summary": "📱 Enviar mensaje de phishing por ID de usuario",
                    "description": "Envía un mensaje de phishing a un usuario específico por su ID. Crea un evento de tipo MENSAJE y genera un enlace para que el usuario pueda reportar la falla. Soporta múltiples medios y proveedores: Telegram (bot), WhatsApp (twilio, selenium, whapi), SMS (twilio).",
                    "tags": ["💬 Mensajes"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/MensajeEnviarID"},
                                "examples": {
                                    "telegram_bot": {
                                        "summary": "Telegram con Bot (✅ Funciona)",
                                        "value": {
                                            "medio": "telegram",
                                            "proveedor": "bot",
                                            "idUsuario": 1,
                                            "mensaje": "Hola"
                                        }
                                    },
                                    "whatsapp_whapi": {
                                        "summary": "WhatsApp con whapi (✅ Funciona)",
                                        "value": {
                                            "medio": "whatsapp",
                                            "proveedor": "whapi",
                                            "idUsuario": 1,
                                            "mensaje": "Hola"
                                        }
                                    },
                                    "whatsapp_whapi_link_preview": {
                                        "summary": "WhatsApp con whapi Link Preview (✅ Funciona)",
                                        "value": {
                                            "medio": "whatsapp",
                                            "proveedor": "whapi-link-preview",
                                            "idUsuario": 1,
                                            "mensaje": "Hola"
                                        }
                                    },
                                    "whatsapp_twilio": {
                                        "summary": "WhatsApp con Twilio (⚠️ Limitado)",
                                        "value": {
                                            "medio": "whatsapp",
                                            "proveedor": "twilio",
                                            "idUsuario": 1,
                                            "mensaje": "Hola"
                                        }
                                    },
                                    "whatsapp_selenium": {
                                        "summary": "WhatsApp con Selenium (❌ No funciona)",
                                        "value": {
                                            "medio": "whatsapp",
                                            "proveedor": "selenium",
                                            "idUsuario": 1,
                                            "mensaje": "Hola"
                                        }
                                    },
                                    "sms_twilio": {
                                        "summary": "SMS con Twilio (⚠️ Limitado)",
                                        "value": {
                                            "medio": "sms",
                                            "proveedor": "twilio",
                                            "idUsuario": 1,
                                            "mensaje": "Hola"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Mensaje enviado correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {"type": "string"},
                                            "idEvento": {"type": "integer", "description": "ID del evento creado"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {"description": "Solicitud inválida - Faltan campos obligatorios o medio/proveedor inválido"},
                        "404": {"description": "Usuario no encontrado o sin teléfono registrado"},
                        "500": {"description": "Error en el servicio o token no configurado"}
                    }
                }
            },
            "/api/telegram/start": {
                "post": {
                    "summary": "🤖 Iniciar Bot de Telegram",
                    "description": "Inicia el bot de Telegram para recibir comandos /start de usuarios y registrar sus chat_ids. El bot se ejecuta en un hilo separado y puede recibir múltiples usuarios simultáneamente.",
                    "tags": ["🤖 Telegram Bot"],
                    "responses": {
                        "200": {
                            "description": "Bot iniciado correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {"type": "string"},
                                            "status": {"type": "string", "enum": ["started", "running", "error"]},
                                            "usuarios_registrados": {"type": "integer", "description": "Número de usuarios ya registrados"}
                                        }
                                    }
                                }
                            }
                        },
                        "500": {"description": "Error al iniciar el bot"}
                    }
                }
            },
            "/api/telegram/stop": {
                "post": {
                    "summary": "🛑 Detener Bot de Telegram",
                    "description": "Detiene el bot de Telegram. Los usuarios registrados permanecen en memoria hasta que se reinicie el servidor.",
                    "tags": ["🤖 Telegram Bot"],
                    "responses": {
                        "200": {
                            "description": "Bot detenido correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {"type": "string"},
                                            "status": {"type": "string", "enum": ["stopped", "error"]}
                                        }
                                    }
                                }
                            }
                        },
                        "500": {"description": "Error al detener el bot"}
                    }
                }
            },
            "/api/telegram/status": {
                "get": {
                    "summary": "📊 Estado del Bot de Telegram",
                    "description": "Obtiene el estado actual del bot de Telegram y la lista de usuarios registrados con sus chat_ids.",
                    "tags": ["🤖 Telegram Bot"],
                    "responses": {
                        "200": {
                            "description": "Estado del bot obtenido correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "is_running": {"type": "boolean", "description": "Si el bot está ejecutándose"},
                                            "usuarios_registrados": {"type": "integer", "description": "Número de usuarios registrados"},
                                            "usuarios": {
                                                "type": "object",
                                                "description": "Diccionario con chat_ids como claves y información de usuarios como valores",
                                                "additionalProperties": {
                                                    "type": "object",
                                                    "properties": {
                                                        "username": {"type": "string"},
                                                        "first_name": {"type": "string"},
                                                        "last_name": {"type": "string"},
                                                        "phone_number": {"type": "string", "nullable": True}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "500": {"description": "Error al obtener el estado"}
                    }
                }
            },
            "/api/telegram/telethon/auth": {
                "post": {
                    "summary": "📱 Autenticar Telethon (Cuenta Propia)",
                    "description": "Autentica Telethon para usar tu cuenta personal de Telegram. El flujo es en etapas: 1) Enviar teléfono → 2) Recibir código en Telegram → 3) Enviar código → 4) (Opcional) Enviar contraseña 2FA. La sesión se guarda en la base de datos para uso futuro.",
                    "tags": ["📱 Telegram Account"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "phone": {
                                            "type": "string",
                                            "description": "Número de teléfono con código de país (ej: +5491168148355). Requerido en etapa 1.",
                                            "example": "+5491168148355"
                                        },
                                        "code": {
                                            "type": "string",
                                            "description": "Código de verificación recibido en Telegram. Requerido en etapa 2.",
                                            "example": "12345"
                                        },
                                        "password": {
                                            "type": "string",
                                            "description": "Contraseña de autenticación de dos factores (2FA). Requerido solo si se activó 2FA en la cuenta.",
                                            "example": "mi_password_2fa"
                                        }
                                    }
                                },
                                "examples": {
                                    "etapa1": {
                                        "summary": "Etapa 1: Enviar teléfono",
                                        "value": {"phone": "+5491168148355"}
                                    },
                                    "etapa2": {
                                        "summary": "Etapa 2: Enviar código",
                                        "value": {"phone": "+5491168148355", "code": "12345"}
                                    },
                                    "etapa3": {
                                        "summary": "Etapa 3: Enviar contraseña 2FA (si aplica)",
                                        "value": {"phone": "+5491168148355", "code": "12345", "password": "mi_password_2fa"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Respuesta según etapa de autenticación",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {
                                                "type": "string",
                                                "enum": ["code_sent", "password_required", "authenticated"],
                                                "description": "Estado de la autenticación"
                                            },
                                            "message": {
                                                "type": "string",
                                                "description": "Mensaje descriptivo del estado"
                                            },
                                            "phone": {
                                                "type": "string",
                                                "description": "Teléfono utilizado (solo en algunas respuestas)"
                                            }
                                        }
                                    },
                                    "examples": {
                                        "code_sent": {
                                            "summary": "Código enviado",
                                            "value": {
                                                "status": "code_sent",
                                                "message": "Código de verificación enviado a +5491168148355. Por favor, envía el código recibido.",
                                                "phone": "+5491168148355"
                                            }
                                        },
                                        "password_required": {
                                            "summary": "Se requiere contraseña 2FA",
                                            "value": {
                                                "status": "password_required",
                                                "message": "Se requiere contraseña de autenticación de dos factores. Por favor, envía la contraseña.",
                                                "phone": "+5491168148355"
                                            }
                                        },
                                        "authenticated": {
                                            "summary": "Autenticación exitosa",
                                            "value": {
                                                "status": "authenticated",
                                                "message": "Autenticación exitosa. Sesión guardada."
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Error en la solicitud (datos insuficientes, teléfono no coincide, etc.)",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        },
                        "500": {
                            "description": "Error en el servidor o credenciales no configuradas",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/ngrok/crear-tunel": {
                "post": {
                    "summary": "🌐 Crear túnel ngrok temporal",
                    "description": "Crea un túnel temporal de ngrok para exponer el servidor local. Requiere que ngrok esté instalado y configurado con el token correspondiente.",
                    "tags": ["🌐 Ngrok"],
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/NgrokCrearTunel"},
                                "example": {
                                    "puerto": 8080
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Túnel ngrok creado exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {"type": "string"},
                                            "url_publica": {"type": "string", "description": "URL pública del túnel ngrok"},
                                            "puerto_local": {"type": "integer", "description": "Puerto local expuesto"},
                                            "proceso_id": {"type": "integer", "description": "ID del proceso ngrok"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {"description": "ngrok no está instalado o no está en el PATH"},
                        "500": {"description": "Error al configurar ngrok, token no configurado o error inesperado"}
                    }
                }
            },
            "/api/ngrok/obtener-url": {
                "get": {
                    "summary": "🔍 Obtener URL del túnel ngrok activo",
                    "description": "Obtiene la URL del túnel ngrok actualmente activo. Consulta la API local de ngrok en el puerto 4040.",
                    "tags": ["🌐 Ngrok"],
                    "responses": {
                        "200": {
                            "description": "URL del túnel ngrok obtenida correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {"type": "string"},
                                            "url_publica": {"type": "string", "description": "URL pública del túnel ngrok"},
                                            "estado": {"type": "string", "description": "Estado del túnel"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {"description": "No hay túneles ngrok activos"},
                        "500": {"description": "Error al consultar la API de ngrok"}
                    }
                }
            },
            "/api/ngrok/cerrar-tuneles": {
                "delete": {
                    "summary": "🛑 Cerrar todos los túneles ngrok",
                    "description": "Cierra todos los túneles ngrok activos. Útil para limpiar recursos y liberar puertos.",
                    "tags": ["🌐 Ngrok"],
                    "responses": {
                        "200": {
                            "description": "Túneles ngrok cerrados exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {"type": "string"},
                                            "tuneles_cerrados": {"type": "integer", "description": "Número de túneles cerrados"}
                                        }
                                    }
                                }
                            }
                        },
                        "500": {"description": "Error al consultar o cerrar túneles ngrok"}
                    }
                }
            },
            "/api/eventos/batch-prueba": {
                "post": {
                    "summary": "Crear batch de eventos de prueba",
                    "description": "Crea un conjunto de eventos de phishing de prueba para los empleados especificados. Los eventos incluyen diferentes tipos (correo, mensaje, llamada) con fechas personalizables. Los usuarios 1-6 tienen distribución normal (40% fallas activas, 20% reportados, 40% pendientes). Los usuarios 7-9 tienen mayor probabilidad de reportar eventos (10% fallas activas, 20% reportados con falla previa, 50% reportados sin falla previa, 20% pendientes) para ganar puntos. Aproximadamente el 50% de las fallas creadas serán fallas graves (esFallaGrave=true), que restan 10 puntos en lugar de 5.",
                    "tags": ["📅 Eventos"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "usuarios": {
                                            "type": "array",
                                            "items": {"type": "integer"},
                                            "description": "IDs de usuarios a los que aplicar los eventos (por defecto 4-9)",
                                            "example": [4, 5, 6, 7, 8, 9]
                                        },
                                        "eventos": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "tipoEvento": {
                                                        "type": "string",
                                                        "enum": ["CORREO", "MENSAJE", "LLAMADA"],
                                                        "description": "Tipo de evento de phishing"
                                                    },
                                                    "asunto": {
                                                        "type": "string",
                                                        "description": "Título del evento"
                                                    },
                                                    "fechaEvento": {
                                                        "type": "string",
                                                        "format": "date-time",
                                                        "description": "Fecha y hora del evento (formato ISO)"
                                                    },
                                                    "cuerpo": {
                                                        "type": "string",
                                                        "description": "Contenido del cuerpo del evento (para correos)"
                                                    },
                                                    "mensaje": {
                                                        "type": "string",
                                                        "description": "Contenido del mensaje (para SMS/WhatsApp/llamadas)"
                                                    },
                                                    "usuarios": {
                                                        "type": "array",
                                                        "items": {"type": "integer"},
                                                        "description": "IDs específicos de usuarios para este evento (opcional)"
                                                    }
                                                },
                                                "required": ["tipoEvento", "asunto", "fechaEvento"]
                                            },
                                            "description": "Array de eventos a crear"
                                        }
                                    },
                                    "required": ["eventos"]
                                },
                                "example": {
                                    "usuarios": [4, 5, 6, 7, 8, 9],
                                    "eventos": [
                                        {
                                            "tipoEvento": "CORREO",
                                            "asunto": "Oferta especial de trabajo remoto",
                                            "fechaEvento": "2025-09-05T10:30:00",
                                            "cuerpo": "Estimado/a, tenemos una oferta especial de trabajo remoto con excelentes beneficios...",
                                            "usuarios": [4, 5, 6, 7]
                                        },
                                        {
                                            "tipoEvento": "MENSAJE",
                                            "asunto": "Mensaje de WhatsApp",
                                            "fechaEvento": "2025-09-08T11:30:00",
                                            "mensaje": "Hola! Te escribo porque necesito que me confirmes algunos datos de tu cuenta bancaria...",
                                            "usuarios": [5, 6, 7, 8]
                                        },
                                        {
                                            "tipoEvento": "LLAMADA",
                                            "asunto": "Llamada de soporte técnico",
                                            "fechaEvento": "2025-09-10T10:15:00",
                                            "mensaje": "Llamada simulada: 'Buenos días, soy del departamento de soporte técnico...'",
                                            "usuarios": [4, 6, 7, 8, 9]
                                        }
                                    ]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Batch de eventos creado exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {"type": "string", "example": "Batch de eventos creado exitosamente"},
                                            "eventos_creados": {"type": "integer", "example": 10},
                                            "resultados_creados": {"type": "integer", "example": 50},
                                            "eventos": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "idEvento": {"type": "integer"},
                                                        "tipoEvento": {"type": "string", "enum": ["CORREO", "MENSAJE", "LLAMADA"]},
                                                        "fechaEvento": {"type": "string", "format": "date-time"},
                                                        "asunto": {"type": "string"},
                                                        "usuariosAsociados": {"type": "integer"}
                                                    }
                                                }
                                            },
                                            "resumen_resultados": {
                                                "type": "object",
                                                "properties": {
                                                    "fallas_activas": {"type": "integer", "description": "Cantidad total de fallas activas"},
                                                    "fallas_activas_simples": {"type": "integer", "description": "Cantidad de fallas activas simples (restan 5 puntos)"},
                                                    "fallas_activas_graves": {"type": "integer", "description": "Cantidad de fallas activas graves (restan 10 puntos)"},
                                                    "reportados": {"type": "integer", "description": "Cantidad de eventos reportados"},
                                                    "fallas_pasadas": {"type": "integer", "description": "Cantidad total de fallas pasadas"},
                                                    "fallas_pasadas_simples": {"type": "integer", "description": "Cantidad de fallas pasadas simples (penalización de 5 puntos)"},
                                                    "fallas_pasadas_graves": {"type": "integer", "description": "Cantidad de fallas pasadas graves (penalización de 10 puntos)"},
                                                    "pendientes": {"type": "integer", "description": "Cantidad de eventos pendientes sin falla"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "500": {"description": "Error del servidor", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/auth/logout": {
                "post": {
                    "summary": "Cerrar sesión del usuario",
                    "description": "Cierra la sesión del usuario actualmente logueado y limpia los datos de sesión",
                    "tags": ["🔐 Auth"],
                    "responses": {
                        "200": {
                            "description": "Sesión cerrada exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {
                                                "type": "string",
                                                "example": "Sesión cerrada exitosamente"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/auth/current-user": {
                "get": {
                    "summary": "Obtener información del usuario actual",
                    "description": "Obtiene la información del usuario actualmente logueado",
                    "tags": ["🔐 Auth"],
                    "responses": {
                        "200": {
                            "description": "Información del usuario",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "usuario": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "integer", "example": 1},
                                                    "nombre": {"type": "string", "example": "Juan"},
                                                    "apellido": {"type": "string", "example": "Pérez"},
                                                    "email": {"type": "string", "example": "juan.perez@empresa.com"},
                                                    "esAdministrador": {"type": "boolean", "example": False}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "No hay usuario logueado",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "error": {
                                                "type": "string",
                                                "example": "No hay usuario logueado"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/auth/check-session": {
                "get": {
                    "summary": "Verificar estado de la sesión",
                    "description": "Verifica si hay una sesión activa y obtiene información del usuario",
                    "tags": ["🔐 Auth"],
                    "responses": {
                        "200": {
                            "description": "Estado de la sesión",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "isLoggedIn": {"type": "boolean", "example": True},
                                            "isAdmin": {"type": "boolean", "example": False},
                                            "usuario": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "integer", "example": 1},
                                                    "nombre": {"type": "string", "example": "Juan"},
                                                    "apellido": {"type": "string", "example": "Pérez"},
                                                    "email": {"type": "string", "example": "juan.perez@empresa.com"},
                                                    "esAdministrador": {"type": "boolean", "example": False}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/empleado/reportar-evento": {
                "post": {
                    "summary": "Reportar evento de phishing",
                    "description": "Permite a un empleado reportar un evento de phishing. Verifica si el evento existe en usuarioxevento para ese usuario.",
                    "tags": ["👤 Empleados"],
                    "security": [{"sessionAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["tipoEvento", "fechaInicio", "fechaFin"],
                                    "properties": {
                                        "tipoEvento": {
                                            "type": "string",
                                            "enum": ["CORREO", "MENSAJE", "LLAMADA"],
                                            "example": "CORREO",
                                            "description": "Tipo de evento de phishing"
                                        },
                                        "fechaInicio": {
                                            "type": "string",
                                            "format": "date-time",
                                            "example": "2024-01-15T09:00:00Z",
                                            "description": "Fecha y hora de inicio del evento"
                                        },
                                        "fechaFin": {
                                            "type": "string",
                                            "format": "date-time",
                                            "example": "2024-01-15T17:00:00Z",
                                            "description": "Fecha y hora de fin del evento"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Evento reportado exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {
                                                "type": "string",
                                                "example": "¡Gracias por reportar! El evento ha sido verificado correctamente."
                                            },
                                            "verificado": {
                                                "type": "boolean",
                                                "example": True
                                            },
                                            "idIntentoReporte": {
                                                "type": "integer",
                                                "example": 123
                                            },
                                            "resultadoVerificacion": {
                                                "type": "string",
                                                "example": "Evento verificado correctamente. ID: 456"
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Solicitud inválida",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        },
                        "401": {
                            "description": "Debe estar logueado para reportar eventos",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "error": {
                                                "type": "string",
                                                "example": "Debe estar logueado para reportar eventos"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/empleado/mis-reportes": {
                "get": {
                    "summary": "Obtener reportes del empleado",
                    "description": "Obtiene todos los reportes realizados por el empleado logueado",
                    "tags": ["👤 Empleados"],
                    "security": [{"sessionAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Lista de reportes del empleado",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "intentos": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "idIntentoReporte": {"type": "integer", "example": 123},
                                                        "idUsuario": {"type": "integer", "example": 1},
                                                        "tipoEvento": {"type": "string", "example": "CORREO"},
                                                        "fechaInicio": {"type": "string", "format": "date-time"},
                                                        "fechaFin": {"type": "string", "format": "date-time"},
                                                        "fechaIntento": {"type": "string", "format": "date-time"},
                                                        "verificado": {"type": "boolean", "example": True},
                                                        "resultadoVerificacion": {"type": "string"},
                                                        "idEventoVerificado": {"type": "integer", "example": 456}
                                                    }
                                                }
                                            },
                                            "total": {"type": "integer", "example": 5}
                                        }
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Debe estar logueado para ver sus reportes",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "error": {
                                                "type": "string",
                                                "example": "Debe estar logueado para ver sus reportes"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/empleado/scoring": {
                "get": {
                    "summary": "Obtener scoring del empleado",
                    "description": "Obtiene el scoring de phishing awareness del empleado logueado",
                    "tags": ["👤 Empleados"],
                    "security": [{"sessionAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Scoring del empleado",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "scoring": {
                                                "type": "object",
                                                "properties": {
                                                    "puntosActuales": {"type": "integer", "example": 85},
                                                    "nivelRiesgo": {"type": "string", "example": "Riesgo bajo"},
                                                    "totalEventos": {"type": "integer", "example": 10},
                                                    "eventosReportados": {"type": "integer", "example": 7},
                                                    "eventosFallidos": {"type": "integer", "example": 3},
                                                    "fallasActivas": {"type": "integer", "example": 1},
                                                    "fallasPasadas": {"type": "integer", "example": 2},
                                                    "puntosPerdidos": {"type": "integer", "example": 15},
                                                    "puntosGanados": {"type": "integer", "example": 0}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Debe estar logueado para ver su scoring",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "error": {
                                                "type": "string",
                                                "example": "Debe estar logueado para ver su scoring"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/admin/limpiar-bd": {
                "delete": {
                    "summary": "⚠️ LIMPIAR BASE DE DATOS COMPLETAMENTE",
                    "description": "🚨 OPERACIÓN EXTREMADAMENTE PELIGROSA 🚨\n\nElimina TODOS los datos de la base de datos de forma irreversible:\n- Todos los usuarios\n- Todas las áreas\n- Todos los eventos\n- Todos los resultados\n- Todos los intentos de reporte\n\n⚠️ ESTA OPERACIÓN NO SE PUEDE DESHACER ⚠️\n\nSolo disponible para administradores. Usar con extrema precaución.",
                    "tags": ["⚠️ PELIGRO"],
                    "security": [{"sessionAuth": []}],
                    "responses": {
                        "200": {
                            "description": "⚠️ Base de datos eliminada completamente - OPERACIÓN IRREVERSIBLE",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {
                                                "type": "string",
                                                "example": "⚠️ Base de datos limpiada exitosamente - TODOS LOS DATOS HAN SIDO ELIMINADOS"
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Debe estar logueado",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "error": {
                                                "type": "string",
                                                "example": "Debe estar logueado para limpiar la base de datos"
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "403": {
                            "description": "🚫 ACCESO DENEGADO - Solo administradores pueden ejecutar operaciones destructivas",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "error": {
                                                "type": "string",
                                                "example": "🚫 Solo los administradores pueden limpiar la base de datos - OPERACIÓN BLOQUEADA"
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "500": {
                            "description": "💥 Error crítico durante operación destructiva",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "error": {
                                                "type": "string",
                                                "example": "💥 Error crítico limpiando la base de datos: [detalle del error] - OPERACIÓN FALLIDA"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/llamadas/subir-audio": {
                "post": {
                    "summary": "Subir archivo de audio para clonación de voz",
                    "tags": ["📞 Llamadas"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "audio": {
                                            "type": "string",
                                            "format": "binary",
                                            "description": "Archivo de audio en formato webm/mp3"
                                        },
                                        "usuario": {
                                            "type": "string",
                                            "description": "Nombre del usuario"
                                        },
                                        "area": {
                                            "type": "string",
                                            "description": "Área del usuario"
                                        },
                                        "historia": {
                                            "type": "string",
                                            "description": "Historia utilizada para la grabación"
                                        },
                                        "idUsuario": {
                                            "type": "string",
                                            "description": "ID del usuario remitente"
                                        }
                                    },
                                    "required": ["audio"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Audio subido correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "message": {"type": "string"},
                                            "filename": {"type": "string"},
                                            "ubicacion": {"type": "string"},
                                            "usuario": {"type": "string"},
                                            "area": {"type": "string"},
                                            "historia": {"type": "string"},
                                            "idUsuario": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {"description": "Error en la solicitud", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "500": {"description": "Error interno del servidor", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/llamadas/clonar": {
                "post": {
                    "summary": "Clonar voz usando archivo de audio",
                    "tags": ["📞 Llamadas"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "idUsuario": {
                                            "type": "string",
                                            "description": "ID del usuario para asociar la voz clonada"
                                        },
                                        "ubicacionArchivo": {
                                            "type": "string",
                                            "description": "Ruta del archivo de audio a clonar"
                                        }
                                    },
                                    "required": ["idUsuario", "ubicacionArchivo"],
                                    "example": {
                                        "idUsuario": "5",
                                        "ubicacionArchivo": "./audios/GrabacionVozMora.mp3"
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Voz clonada correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "idVoz": {"type": "string", "description": "ID de la voz clonada en ElevenLabs"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {"description": "Error en la solicitud", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "404": {"description": "Usuario no encontrado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "500": {"description": "Error interno del servidor", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/llamadas/check-voz/{idUsuario}": {
                "get": {
                    "summary": "Verificar si un usuario tiene voz configurada",
                    "tags": ["📞 Llamadas"],
                    "parameters": [
                        {
                            "name": "idUsuario",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                            "description": "ID del usuario a verificar"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Estado de la voz del usuario",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "tieneVoz": {"type": "boolean", "description": "Si el usuario tiene voz configurada"},
                                            "idVoz": {"type": "string", "nullable": True, "description": "ID de la voz si existe"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {"description": "Usuario no encontrado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "500": {"description": "Error interno del servidor", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/api/tts": {
                "post": {
                    "summary": "Generar audio de texto a voz usando ElevenLabs",
                    "tags": ["📞 Llamadas"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "idVoz": {
                                            "type": "string",
                                            "description": "ID de la voz a utilizar"
                                        },
                                        "texto": {
                                            "type": "string",
                                            "description": "Texto a convertir a audio"
                                        },
                                        "modelo": {
                                            "type": "string",
                                            "description": "Modelo de ElevenLabs a utilizar",
                                            "default": "eleven_multilingual_v2"
                                        },
                                        "estabilidad": {
                                            "type": "number",
                                            "description": "Estabilidad de la voz (0.0 - 1.0)",
                                            "default": 0.6
                                        },
                                        "velocidad": {
                                            "type": "number",
                                            "description": "Velocidad de la voz (0.0 - 1.0)",
                                            "default": 0.9
                                        },
                                        "exageracion": {
                                            "type": "number",
                                            "description": "Exageración de la voz (0.0 - 1.0)",
                                            "default": 0.5
                                        }
                                    },
                                    "required": ["idVoz", "texto"],
                                    "example": {
                                        "idVoz": "GHUI7Bui6hqAYVXaCoEX",
                                        "texto": "Hola yo soy Marcos y quería avisarles que mañana les voy a mandar un mail, por favor avísenme cuando lo reciban.",
                                        "modelo": "eleven_multilingual_v2",
                                        "estabilidad": 0.6,
                                        "velocidad": 0.9,
                                        "exageracion": 0.5
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Audio generado correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {"type": "string"},
                                            "idAudio": {"type": "string"},
                                            "ubicacion": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {"description": "Error en la solicitud", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "500": {"description": "Error interno del servidor", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "ResultadoEvento": {
                    "type": "string",
                    "enum": ["PENDIENTE", "REPORTADO", "FALLA"]
                },
                "TipoEvento": {
                    "type": "string",
                    "enum": ["LLAMADA", "CORREO", "MENSAJE"]
                },
                "RegistroEvento": {
                    "type": "object",
                    "properties": {
                        "idRegistroEvento": {"type": "integer"},
                        "asunto": {"type": "string"},
                        "cuerpo": {"type": "string"}
                    }
                },
                "Evento": {
                    "type": "object",
                    "properties": {
                        "idEvento": {"type": "integer"},
                        "tipoEvento": {"$ref": "#/components/schemas/TipoEvento"},
                        "fechaEvento": {"type": "string", "format": "date-time"},
                        "registroEvento": {"$ref": "#/components/schemas/RegistroEvento"},
                        "usuarios": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "idUsuario": {"type": "integer"},
                                    "nombreUsuario": {"type": "string"},
                                    "resultado": {"$ref": "#/components/schemas/ResultadoEvento"},
                                    "fechaReporte": {"type": "string", "format": "date-time", "description": "Fecha del reporte (si existe)"},
                                    "fechaFalla": {"type": "string", "format": "date-time", "description": "Fecha de la falla (si existe)"},
                                    "haFalladoEnElPasado": {"type": "boolean", "description": "Indica si el usuario ha fallado en el pasado en algún evento"},
                                    "esFallaGrave": {"type": "boolean", "description": "Indica si la falla fue grave (resta 10 puntos) o simple (resta 5 puntos)"}
                                }
                            }
                        }
                    }
                },
                "EventoCreate": {
                    "type": "object",
                    "required": ["tipoEvento", "fechaEvento"],
                    "properties": {
                        "tipoEvento": {"$ref": "#/components/schemas/TipoEvento"},
                        "fechaEvento": {"type": "string", "format": "date-time"},
                        "registroEvento": {"type": "object", "properties": {"asunto": {"type": "string"}, "cuerpo": {"type": "string"}}}
                    }
                },
                "EventoUpdate": {
                    "type": "object",
                    "properties": {
                        "tipoEvento": {"$ref": "#/components/schemas/TipoEvento"},
                        "fechaEvento": {"type": "string", "format": "date-time"},
                        "registroEvento": {"type": "object", "properties": {"asunto": {"type": "string"}, "cuerpo": {"type": "string"}}}
                    }
                },
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
                        "idArea": {"type": "integer", "nullable": True},
                        "perfilLinkedin": {"type": "string", "nullable": True},
                        "idVoz": {"type": "string", "nullable": True, "description": "ID de la voz clonada en ElevenLabs"}
                    }
                },
                "EmpleadoFalla": {
                    "type": "object",
                    "properties": {
                        "idUsuario": {"type": "integer"},
                        "nombre": {"type": "string"},
                        "apellido": {"type": "string"},
                        "cantidadFallas": {"type": "integer"}
                    }
                },
                "AreaFallas": {
                    "type": "object",
                    "properties": {
                        "idArea": {"type": "integer"},
                        "nombreArea": {"type": "string"},
                        "totalFallas": {"type": "integer"},
                        "empleadosConFalla": {"type": "integer"},
                        "empleados": {"type": "array", "items": {"$ref": "#/components/schemas/EmpleadoFalla"}}
                    }
                },
                "Area": {
                    "type": "object",
                    "properties": {
                        "idArea": {"type": "integer"},
                        "nombreArea": {"type": "string"},
                        "datosDelArea": {"type": "array", "items": {"type": "string"}, "nullable": True},
                        "usuarios": {"type": "array", "items": {"$ref": "#/components/schemas/Usuario"}}
                    }
                },
                "AreaCreate": {
                    "type": "object",
                    "required": ["nombreArea", "usuarios"],
                    "properties": {
                        "nombreArea": {"type": "string"},
                        "usuarios": {"type": "array", "items": {"type": "integer"}},
                        "datosArea": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "AreaUpdate": {
                    "type": "object",
                    "properties": {
                        "nombreArea": {"type": "string"},
                        "datosDelArea": {"type": "array", "items": {"type": "string"}}
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
                        "idArea": {"type": "integer"},
                        "perfilLinkedin": {"type": "string"}
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
                        "idArea": {"type": "integer"},
                        "perfilLinkedin": {"type": "string"},
                        "idVoz": {"type": "string", "nullable": True, "description": "ID de la voz clonada en ElevenLabs"}
                    }
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "codigo": {"type": "string"},
                        "descripcion": {"type": "string"}
                    }
                },
                "EmailEnviarID": {
                    "type": "object",
                    "required": ["proveedor", "idUsuarioDestinatario", "asunto", "cuerpo", "dificultad"],
                    "properties": {
                        "proveedor": {"type": "string", "enum": ["twilio", "smtp"]},
                        "idUsuarioDestinatario": {"type": "integer", "description": "ID del usuario destinatario del email"},
                        "idUsuarioRemitente": {"type": "integer", "description": "ID del usuario remitente - requerido solo para dificultad Difícil"},
                        "asunto": {"type": "string"},
                        "cuerpo": {"type": "string"},
                        "dificultad": {"type": "string", "enum": ["Fácil", "Medio", "Difícil"], "description": "Nivel de dificultad del email de phishing"}
                    }
                },
                "EmailGenerar": {
                    "type": "object",
                    "required": ["contexto"],
                    "properties": {
                        "contexto": {"type": "string"},
                        "formato": {"type": "string"},
                        "nivel": {"type": "integer", "minimum": 1, "maximum": 3}
                    }
                },
                "EmailNotificar": {
                    "type": "object",
                    "required": ["destinatario", "asunto", "cuerpo"],
                    "properties": {
                        "destinatario": {"type": "string"},
                        "asunto": {"type": "string"},
                        "cuerpo": {"type": "string"}
                    }
                },
                "MensajeWhatsApp": {
                    "type": "object",
                    "required": ["remitente", "destinatario", "mensaje"],
                    "properties": {
                        "remitente": {"type": "string", "description": "Número de teléfono del remitente (formato internacional)"},
                        "destinatario": {"type": "string", "description": "Número de teléfono del destinatario (formato internacional)"},
                        "mensaje": {"type": "string", "description": "Contenido del mensaje"}
                    }
                },
                "MensajeSMS": {
                    "type": "object",
                    "required": ["remitente", "destinatario", "mensaje"],
                    "properties": {
                        "remitente": {"type": "string", "description": "Número de teléfono del remitente (formato internacional)"},
                        "destinatario": {"type": "string", "description": "Número de teléfono del destinatario (formato internacional)"},
                        "mensaje": {"type": "string", "description": "Contenido del mensaje"}
                    }
                },
                "MensajeWhatsAppSelenium": {
                    "type": "object",
                    "required": ["destinatario", "mensaje"],
                    "properties": {
                        "destinatario": {"type": "string", "description": "Número de teléfono o nombre del contacto (ej: 'Marcos Gurruchaga' o '+54 9 11 4163-5935')"},
                        "mensaje": {"type": "string", "description": "Contenido del mensaje a enviar"}
                    }
                },
                "MensajeWhapiCloud": {
                    "type": "object",
                    "required": ["mensaje"],
                    "properties": {
                        "mensaje": {"type": "string", "description": "Contenido del mensaje a enviar"},
                        "destinatario": {"type": "string", "description": "Número de teléfono del destinatario (formato internacional). Si no se especifica, se usa +54 9 11 4163-5935 por defecto. El sistema formatea automáticamente números argentinos al formato 549XXXXXXXXX"}
                    }
                },
                "MensajeWhapiGrupo": {
                    "type": "object",
                    "required": ["mensaje"],
                    "properties": {
                        "mensaje": {"type": "string", "description": "Contenido del mensaje a enviar al grupo"},
                        "grupo_id": {"type": "string", "description": "ID del grupo de WhatsApp. Si no se especifica, se usa '120363416003158863@g.us' por defecto. El grupo_id debe ser el identificador único del grupo de WhatsApp"}
                    }
                },
                "MensajeGenerar": {
                    "type": "object",
                    "required": ["contexto"],
                    "properties": {
                        "contexto": {"type": "string", "description": "Contexto para generar el mensaje (área, usuario, fecha, etc.)"},
                        "nivel": {"type": "string", "enum": ["Fácil", "Medio", "Difícil"], "description": "Nivel de dificultad del mensaje de phishing"}
                    }
                },
                "MensajeEnviarID": {
                    "type": "object",
                    "required": ["medio", "idUsuario", "mensaje"],
                    "properties": {
                        "medio": {"type": "string", "enum": ["telegram", "whatsapp", "sms"], "description": "Medio de comunicación (telegram, whatsapp, sms)"},
                        "proveedor": {"type": "string", "description": "Proveedor específico dentro del medio. Para telegram: 'bot'. Para whatsapp: 'twilio', 'selenium', 'whapi', 'whapi-link-preview'. Para sms: 'twilio'"},
                        "idUsuario": {"type": "integer", "description": "ID del usuario al que se enviará el mensaje"},
                        "mensaje": {"type": "string", "description": "Contenido del mensaje de phishing a enviar"}
                    }
                },
                "NgrokCrearTunel": {
                    "type": "object",
                    "properties": {
                        "puerto": {"type": "integer", "description": "Puerto local al que hacer túnel (por defecto 8080)", "default": 8080, "minimum": 1, "maximum": 65535}
                    }
                },
                "SumarFalla": {
                    "type": "object",
                    "required": ["idUsuario", "idEvento"],
                    "properties": {
                        "idUsuario": {"type": "integer", "description": "ID del usuario"},
                        "idEvento": {"type": "integer", "description": "ID del evento"},
                        "fechaFalla": {"type": "string", "format": "date-time", "description": "Fecha de la falla (OPCIONAL - si no se proporciona se usa la fecha y hora actual automáticamente)"}
                    }
                },
                "SumarFallaGrave": {
                    "type": "object",
                    "required": ["idUsuario", "idEvento"],
                    "properties": {
                        "idUsuario": {"type": "integer", "description": "ID del usuario"},
                        "idEvento": {"type": "integer", "description": "ID del evento"},
                        "fechaFalla": {"type": "string", "format": "date-time", "description": "Fecha de la falla grave (OPCIONAL - si no se proporciona se usa la fecha y hora actual automáticamente)"}
                    }
                },
                "SumarReportado": {
                    "type": "object",
                    "required": ["idUsuario", "idEvento"],
                    "properties": {
                        "idUsuario": {"type": "integer", "description": "ID del usuario"},
                        "idEvento": {"type": "integer", "description": "ID del evento"},
                        "fechaReporte": {"type": "string", "format": "date-time", "description": "Fecha del reporte (OPCIONAL - si no se proporciona se usa la fecha y hora actual automáticamente)"}
                    }
                },
                "AsociarUsuarioEvento": {
                    "type": "object",
                    "required": ["resultado"],
                    "properties": {
                        "resultado": {"$ref": "#/components/schemas/ResultadoEvento", "description": "Estado actual del evento para este usuario"},
                        "fechaReporte": {"type": "string", "format": "date-time", "description": "Fecha del reporte (OPCIONAL)"},
                        "fechaFalla": {"type": "string", "format": "date-time", "description": "Fecha de la falla (OPCIONAL)"}
                    }
                }
            },
            # "securitySchemes": {
            #     "sessionAuth": {
            #         "type": "apiKey",
            #         "in": "cookie",
            #         "name": "session",
            #         "description": "Autenticación basada en sesión de Flask"
            #     }
            # }
        }
    }
    return jsonify(spec)


@swagger.route("/api/swagger", methods=["GET"])
def swagger_ui():
    html = """
<!DOCTYPE html>
<html lang=\"es\">
  <head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>PhishIntel Swagger</title>
    <link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist@5/swagger-ui.css\" />
    <link rel=\"stylesheet\" href=\"/api/swagger-styles\" />
    <style>
      body { 
        margin: 0; 
        padding: 0; 
        background-color: #1a1a1a;
        color: #ffffff;
      } 
      #swagger-ui { 
        width: 100%; 
      }
    </style>
  </head>
  <body>
    <div id=\"swagger-ui\"></div>
    <script src=\"https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js\"></script>
    <script>
      window.ui = SwaggerUIBundle({
        url: '/api/openapi.json',
        dom_id: '#swagger-ui',
        presets: [SwaggerUIBundle.presets.apis],
        layout: 'BaseLayout',
        tagsSorter: function(a, b) { return 0; },
        operationsSorter: 'alpha',
        defaultModelsExpandDepth: -1,
        defaultModelExpandDepth: -1,
        docExpansion: 'none',
        tryItOutEnabled: true,
        requestInterceptor: function(request) {
          return request;
        },
        responseInterceptor: function(response) {
          return response;
        },
        onComplete: function() {
          // Activar "Try it out" automáticamente
          setTimeout(function() {
            // Hacer clic automáticamente en todos los botones "Try it out"
            const tryItOutButtons = document.querySelectorAll('.try-out__btn');
            tryItOutButtons.forEach(function(btn) {
              if (!btn.classList.contains('cancel')) {
                btn.click();
              }
            });
            
            // Ocultar los botones "Try it out" después de activarlos
            setTimeout(function() {
              const tryItOutButtons = document.querySelectorAll('.try-out__btn');
              tryItOutButtons.forEach(function(btn) {
                if (!btn.classList.contains('cancel')) {
                  btn.style.display = 'none';
                }
              });
            }, 200);
          }, 500);
        }
      });
    </script>
  </body>
</html>
"""
    return html


@swagger.route("/api/swagger-styles", methods=["GET"])
def swagger_styles():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "assets", "css", "estilosSwagger.css")
    return send_file(css_path, mimetype="text/css")


