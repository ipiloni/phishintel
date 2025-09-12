from flask import Blueprint, jsonify

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
            {"name": "Usuarios", "description": "Gestión de usuarios"},
            {"name": "Áreas", "description": "Gestión de áreas"},
            {"name": "Eventos", "description": "Gestión de eventos"},
            {"name": "Emails", "description": "Envío de emails y notificaciones"},
            {"name": "Mensajes", "description": "Envío de mensajes WhatsApp y SMS"}
        ],
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
            "/api/usuarios/batch": {
                "post": {
                    "summary": "Crear múltiples usuarios",
                    "tags": ["Usuarios"],
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
                    "tags": ["Usuarios"],
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
            ,
            "/api/areas": {
                "get": {
                    "summary": "Obtener todas las áreas",
                    "tags": ["Áreas"],
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
                    "tags": ["Áreas"],
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
                    "tags": ["Áreas"],
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
                    "tags": ["Áreas"],
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
                    "tags": ["Áreas"],
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
                    "tags": ["Áreas"],
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
                    "summary": "Obtener fallas por área (agregado por empleados)",
                    "tags": ["Áreas"],
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
            }
            ,
            "/api/eventos": {
                "get": {
                    "summary": "Obtener todos los eventos",
                    "tags": ["Eventos"],
                    "responses": {
                        "200": {
                            "description": "Lista de eventos",
                            "content": {"application/json": {"schema": {"type": "object", "properties": {"eventos": {"type": "array", "items": {"$ref": "#/components/schemas/Evento"}}}}}}
                        }
                    }
                },
                "post": {
                    "summary": "Crear un evento",
                    "tags": ["Eventos"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/EventoCreate"},
                                "example": {
                                    "tipoEvento": "CORREO",
                                    "fechaEvento": "2025-08-11T10:30:00",
                                    "resultado": "PENDIENTE",
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
                    "tags": ["Eventos"],
                    "parameters": [{"name": "idEvento", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {"200": {"description": "Evento", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Evento"}}}}, "404": {"description": "No encontrado"}}
                },
                "put": {
                    "summary": "Editar un evento",
                    "tags": ["Eventos"],
                    "parameters": [{"name": "idEvento", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/EventoUpdate"}}}},
                    "responses": {"200": {"description": "Evento editado"}, "404": {"description": "No encontrado"}}
                },
                "delete": {
                    "summary": "Eliminar un evento",
                    "tags": ["Eventos"],
                    "parameters": [{"name": "idEvento", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {"200": {"description": "Evento eliminado"}, "404": {"description": "No encontrado"}}
                }
            },
            "/api/eventos/{idEvento}/usuarios/{idUsuario}": {
                "post": {
                    "summary": "Asociar usuario a evento con resultado",
                    "tags": ["Eventos"],
                    "parameters": [
                        {"name": "idEvento", "in": "path", "required": True, "schema": {"type": "integer"}},
                        {"name": "idUsuario", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "required": ["resultado"], "properties": {"resultado": {"$ref": "#/components/schemas/ResultadoEvento"}}}}}},
                    "responses": {"200": {"description": "Asociado"}, "400": {"description": "Solicitud inválida"}, "404": {"description": "No encontrado"}}
                }
            },
            "/api/email/enviar-id": {
                "post": {
                    "summary": "Enviar email por ID de usuario",
                    "tags": ["Emails"],
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
                    "tags": ["Emails"],
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
                    "tags": ["Emails"],
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
                    "summary": "Enviar mensaje por WhatsApp (Twilio) - NO FUNCIONAL",
                    "description": "⚠️ Este endpoint no funciona correctamente actualmente",
                    "tags": ["Mensajes"],
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
                    "summary": "Enviar mensaje por SMS",
                    "tags": ["Mensajes"],
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
                    "summary": "Enviar mensaje por WhatsApp usando Selenium - NO FUNCIONAL",
                    "description": "⚠️ Este endpoint no funciona correctamente actualmente. Envía un mensaje de WhatsApp usando Selenium WebDriver. Requiere que el usuario esté previamente logueado en WhatsApp Web en Chrome Profile 14.",
                    "tags": ["Mensajes"],
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
                    "summary": "Enviar mensaje por WhatsApp usando whapi.cloud",
                    "description": "Envía un mensaje de WhatsApp usando la API de whapi.cloud. Si no se especifica destinatario, se envía al número por defecto +54 9 11 4163-5935. El sistema formatea automáticamente los números argentinos al formato requerido (549XXXXXXXXX).",
                    "tags": ["Mensajes"],
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
                                    "resultado": {"$ref": "#/components/schemas/ResultadoEvento"}
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
                        "registroEvento": {"type": "object", "properties": {"asunto": {"type": "string"}, "cuerpo": {"type": "string"}}},
                        "idUsuario": {"type": "integer"},
                        "resultado": {"$ref": "#/components/schemas/ResultadoEvento"}
                    }
                },
                "EventoUpdate": {
                    "type": "object",
                    "properties": {
                        "tipoEvento": {"$ref": "#/components/schemas/TipoEvento"},
                        "fechaEvento": {"type": "string", "format": "date-time"},
                        "resultado": {"$ref": "#/components/schemas/ResultadoEvento"},
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
        layout: 'BaseLayout',
        tagsSorter: function(a, b) { return 0; },
        operationsSorter: 'alpha'
      });
    </script>
  </body>
</html>
"""
    return html


