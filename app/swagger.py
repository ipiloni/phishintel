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
            {"name": "🏢 Áreas", "description": "Gestión de áreas"},
            {"name": "📅 Eventos", "description": "Gestión de eventos"},
            {"name": "📊 Reportes", "description": "Reportes y métricas de fallas por área y empleado"},
            {"name": "📧 Emails", "description": "Envío de emails y notificaciones"},
            {"name": "💬 Mensajes", "description": "Envío de mensajes WhatsApp y SMS"},
            {"name": "🤖 Telegram Bot", "description": "Gestión del bot de Telegram"},
            {"name": "🌐 Ngrok", "description": "Gestión de túneles ngrok temporales"}
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
                                        "nombreUsuario": "nachoscocco",
                                        "password": "ignacio.scocco1",
                                        "nombre": "Ignacio",
                                        "apellido": "Scocco",
                                        "correo": "ignacio.scocco@pgcontrol.com.ar"
                                    },
                                    {
                                        "nombreUsuario": "manuginobili",
                                        "password": "manuel.ginobili1",
                                        "nombre": "Manuel",
                                        "apellido": "Ginobili",
                                        "correo": "manuel.ginobili@pgcontrol.com.ar"
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
                                    "enum": ["CORREO", "MENSAJE", "LLAMADA", "VIDEOLLAMADA"]
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
                                    "enum": ["CORREO", "MENSAJE", "LLAMADA", "VIDEOLLAMADA"]
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
                                    "enum": ["CORREO", "MENSAJE", "LLAMADA", "VIDEOLLAMADA"]
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
                    "summary": "Marcar evento como falla (usa fecha actual por defecto)",
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
                            "description": "Falla registrada correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "mensaje": {"type": "string"},
                                            "idUsuario": {"type": "integer"},
                                            "idEvento": {"type": "integer"},
                                            "fechaFalla": {"type": "string", "format": "date-time"}
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
                    "summary": "Enviar email por ID de usuario",
                    "tags": ["📧 Emails"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/EmailEnviarID"},
                                "example": {
                                    "proveedor": "twilio",
                                    "idUsuario": 1,
                                    "asunto": "Notificación importante",
                                    "cuerpo": "<p>Este es un email de prueba</p>"
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
                    "enum": ["LLAMADA", "CORREO", "MENSAJE", "VIDEOLLAMADA"]
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
                                    "fechaFalla": {"type": "string", "format": "date-time", "description": "Fecha de la falla (si existe)"}
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
                        "idArea": {"type": "integer", "nullable": True}
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
                },
                "EmailEnviarID": {
                    "type": "object",
                    "required": ["proveedor", "idUsuario", "asunto", "cuerpo"],
                    "properties": {
                        "proveedor": {"type": "string", "enum": ["twilio", "smtp"]},
                        "idUsuario": {"type": "integer"},
                        "asunto": {"type": "string"},
                        "cuerpo": {"type": "string"}
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
            }
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
    css_path = os.path.join(os.path.dirname(__file__), "frontend", "assets", "css", "estilosSwagger.css")
    return send_file(css_path, mimetype="text/css")


