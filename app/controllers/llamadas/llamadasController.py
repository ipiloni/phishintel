import json
from datetime import datetime

from flask import Response, jsonify, current_app
from twilio.twiml.voice_response import Gather, VoiceResponse

from app.backend.apis.elevenLabs import elevenLabs
from app.backend.apis.twilio import twilio
from app.backend.models.error import responseError
from app.backend.models.tipoEvento import TipoEvento
from app.controllers.abm.areasController import AreasController
from app.controllers.abm.eventosController import EventosController
from app.controllers.abm.usuariosController import UsuariosController
from app.controllers.aiController import AIController
from app.controllers.emails.emailController import EmailController
from app.controllers.mensajes.msjController import MsjController
from app.controllers.resultadoEventoController import ResultadoEventoController
from app.utils.config import get
from app.utils import conversacion
from app.utils.conversacion import idEvento
from app.utils.logger import log
import threading

password = get("LLAMAR_PASSWORD")
host_raw = get("URL_APP")

# Normalizar la URL para asegurar que tenga protocolo
if host_raw:
    host = host_raw.strip()
    if not host.startswith("http://") and not host.startswith("https://"):
        # Si es localhost o 127.0.0.1, usar http, sino https
        if "localhost" in host.lower() or "127.0.0.1" in host:
            host = f"http://{host}"
        else:
            host = f"https://{host}"
else:
    host = "http://localhost:8080"  # fallback

nroRemitente = get("NRO_REMITENTE")

class LlamadasController:

    @staticmethod
    def generarLlamada(data):
        """
            recibe los siguientes valores dentro de data:
                password
                idUsuarioDestinatario
                idUsuarioRemitente
                eventoDesencadenador
                rolAImitar
                objetivoEspecifico
            ===================================================================
            1. Revisar a quien estamos llamando, debe ser un usuario de la base.
            2. Crear el evento llamada
            3. Asociarlo al usuario
            4. Generar la conversacion
            5. Guardar en la base el evento
            6. Llamar usuario
            7. Crear un hilo contador que, al pasar los 3/4 minutos, analice la variable conversacionActual, analice con IA si se nombro algo del objetivo y en base a eso genere un nuevo evento.
            8. Luego en otro metodo (al obtener la respuesta del usuario), guardar nuevamente en el evento la conversacion (actualizarla)
        """
        response = LlamadasController.validarRequestLlamada(data)

        if response is not None:
            return response

        idUsuarioDestinatario = data["idUsuarioDestinatario"]
        idUsuarioRemitente = data["idUsuarioRemitente"]

        # Reinicio y seteo variables globales de la conversacion
        conversacion.hilo = False
        conversacion.destinatario = idUsuarioDestinatario
        conversacion.remitente = idUsuarioRemitente
        conversacion.objetivoEspecifico = data["objetivoEspecifico"] # Es un TipoEvento que se usa para generar el evento posterior

        # Obtengo usuarios de la base
        remitente, statusRemitente = UsuariosController.obtenerUsuario(idUsuarioRemitente)
        usuario, statusUsuario = UsuariosController.obtenerUsuario(idUsuarioDestinatario)

        # Se validan las respuestas de la base
        if statusRemitente != 200:
            log.warning("No se encontro un idUsuarioRemitente existente")
            return responseError("USUARIO_INEXISTENTE", "No se encontro un idUsuarioRemitente existente", 400)

        if statusUsuario != 200:
            log.warning("No se encontro un idUsuarioDestinatario existente")
            return responseError("USUARIO_INEXISTENTE", "No se encontro un idUsuarioDestinatario existente", 400)

        # Obtengo los valores de los usuarios consultados
        remitente = remitente.get_json()
        usuario = usuario.get_json()

        # Se obtiene el area del usuario
        area, statusArea = AreasController.obtenerArea(usuario["idArea"])
        if statusArea != 200:
            log.warning("El usuario no pertenece a ningun Area particular")
            return responseError("AREA_INEXISTENTE", f"El usuario de id: {idUsuarioDestinatario} debe pertenecer a un area para generar la llamada", 400)

        area = area.get_json()

        destinatario = usuario["telefono"]
        
        # Validar que el destinatario tenga un número de teléfono válido
        if not destinatario or not str(destinatario).strip():
            log.warning(f"El usuario {idUsuarioDestinatario} no tiene un número de teléfono válido")
            return responseError("TELEFONO_INVALIDO", f"El usuario de id: {idUsuarioDestinatario} no tiene un número de teléfono válido", 400)

        # Elimino de la variable global la conversacion anterior
        conversacion.conversacionActual.clear()

        nombreRemitente = remitente["nombre"] + " " + remitente["apellido"]
        nombreEmpleado = usuario["nombre"] + " " + usuario["apellido"]

        rolAImitar = data["rolAImitar"]
        objetivoEspecifico = data["objetivoEspecifico"]
        eventoDesencadenador = data["eventoDesencadenador"]
        conversacion.eventoDesencadenador = eventoDesencadenador
        conversacion.nombreEmpleado = nombreEmpleado

        conversacion.objetivoActual = f"""
            Eres un actor interpretando un rol. NO eres un asistente de IA.
            Tu rol es: '{rolAImitar}' dentro de la empresa 'PG Control'.
            Tu nombre en esta simulación es: '{nombreRemitente}'.
            El empleado (usuario) se llama {nombreEmpleado}, trabaja en 'PG Control' en el área de {area["nombreArea"]}.
            Tu dialecto: Eres de Buenos Aires, Argentina. El uso del 'vos', el 'che' y el tono porteño es crucial.
            
            El objetivo es simular un intento de phishing telefónico para un entrenamiento de seguridad.
            Debes ser convincente, pero no agresivo, usando urgencia laboral.
            Tu meta es que el empleado {objetivoEspecifico} {eventoDesencadenador} inmediatamente después de cortar esta llamada.
            Tu pretexto es avisarle que le vas a mandar algo urgente y que necesitás que lo abra ni bien se lo mandes porque es urgente.

            Reglas:
            - Tu respuesta debe ser única y exclusivamente el diálogo hablado por tu rol ('{nombreRemitente}').
            - NUNCA incluyas prefijos (ej: `IA:`, `{nombreRemitente}:`, `Respuesta:`).
            - NUNCA incluyas narración, acotaciones (ej: `sonríe`, `duda`) ni explicaciones fuera del personaje.
            - Responde solo con una frase corta que la persona diría en este momento. No te adelantes en la conversación.
            - Mantén siempre el rol de '{rolAImitar}'. Jamás reveles que esto es un entrenamiento.
            - Si la conversación está vacía, empieza con un saludo casual y directo y espera la respuesta.
            - La llamada se esta realizando en este mismo momento (tiempo real).
            
            La conversación hasta ahora es la siguiente:
        """

        log.info(f"La Conversacion actual es la siguiente: {conversacion.conversacionActual}")

        texto = AIController.armarMensajeLlamada(conversacion.objetivoActual, conversacion.conversacionActual)

        log.info(f"La IA genero el texto: {texto}")

        conversacion.conversacionActual.append({"rol": "IA", "mensaje": texto})

        dataEvento = {
            "tipoEvento": "LLAMADA",
            "registroEvento": {
                "objetivo": " ".join(conversacion.objetivoActual.split()).strip(),  # elimina doble espacios y \n
                "remitente": nombreRemitente  # Guardar el nombre del remitente
            }
        }

        log.info(f"{dataEvento}")

        resp = EventosController.crearEvento(dataEvento)

        if isinstance(resp, tuple):
            responseEvento, statusResponse = resp
        else:
            responseEvento = resp
            statusResponse = resp.status_code

        if statusResponse != 201:
            log.error(f"Hubo un error al crear el evento: {responseEvento.get_data(as_text=True)}")
            return responseEvento, statusResponse

        data = responseEvento.get_json()
        conversacion.idEvento = data["idEvento"]

        log.info("Evento creado correctamente, creamos el Usuario por Evento")

        responseUsuarioEvento, statusUsuarioEvento = EventosController.asociarUsuarioEvento(conversacion.idEvento, idUsuarioDestinatario, "PENDIENTE")
        responseUsuarioEvento = responseUsuarioEvento.get_json()

        if statusUsuarioEvento != 200:
            log.error(f"Hubo un error al asociar el usuario al evento: {responseUsuarioEvento}")
            return responseUsuarioEvento, statusUsuarioEvento

        log.info(f"Ahora la conversacion actual es la siguiente: {conversacion.conversacionActual}")

        # Obtener el ID de voz del remitente, con log si se usa default
        idVozRemitente = remitente.get("idVoz")
        if idVozRemitente:
            conversacion.idVozActual = idVozRemitente
            log.info(f"Usando ID de voz del remitente: {idVozRemitente}")
        else:
            conversacion.idVozActual = "O1CnH2NGEehfL1nmYACp"
            log.warning(f"No se encontró ID de voz para el remitente {idUsuarioRemitente}, usando voz default: {conversacion.idVozActual}")

        elevenLabsResponse = elevenLabs.tts(texto, conversacion.idVozActual, "eleven_multilingual_v2",None, None, 0.5)

        idAudio = elevenLabsResponse["idAudio"]

        log.info("Ponemos en internet el audio: " + str(idAudio))

        from app.endpoints.apis import exponerAudio
        exponerAudio(f"{idAudio}.mp3")  # expone el archivo .mp3 a internet para que Twilio pueda reproducirlo

        if destinatario == remitente:
            return responseError("CAMPO_INVALIDO", "El destinatario y remitente no pueden ser iguales", 400)

        url = host
        conversacion.urlAudioActual = f"{url}/api/audios/{idAudio}.mp3"

        log.info(f"La URL del audio actual es: {conversacion.urlAudioActual}")

        # Iniciar el hilo que analiza la llamada después de 2 minutos
        # Capturar el contexto de la aplicación antes de crear el hilo
        try:
            # Intentar obtener el contexto desde current_app si está disponible
            app_context = current_app._get_current_object().app_context()
        except RuntimeError:
            # Si no hay contexto activo, importar la app directamente
            from app.main import app
            app_context = app.app_context()
        
        def iniciarAnalisisDespues():
            import time
            # Usar el contexto de la aplicación dentro del hilo
            with app_context:
                log.info(f"[HILO ANÁLISIS] Hilo de análisis iniciado para evento ID: {conversacion.idEvento}, destinatario: {conversacion.destinatario}")
                log.info(f"[HILO ANÁLISIS] Esperando 2 minutos (120 segundos) antes de analizar la llamada...")
                time.sleep(120)  # Esperar 2 minutos (120 segundos)
                log.info(f"[HILO ANÁLISIS] Tiempo de espera completado, iniciando análisis de la llamada...")
                try:
                    LlamadasController.analizarLlamada()
                    log.info(f"[HILO ANÁLISIS] Análisis de llamada completado exitosamente para evento ID: {conversacion.idEvento}")
                except Exception as e:
                    log.error(f"[HILO ANÁLISIS] Error durante el análisis de la llamada: {str(e)}", exc_info=True)
        
        hilo = threading.Thread(target=iniciarAnalisisDespues)
        hilo.daemon = True  # el hilo no bloquea el cierre del programa
        hilo.start()
        log.info(f"[HILO ANÁLISIS] Hilo de análisis creado y ejecutándose en segundo plano")

        return twilio.llamar(destinatario, nroRemitente, host + "/api/twilio/accion")


    @staticmethod
    def procesarRespuesta(speech, confidence):
        try:
            conversacion.hilo=True
            log.info(f"Lo que dijo el usuario fue: {str(speech)}")

            conversacion.conversacionActual.append({"rol": "destinatario", "mensaje": speech})

            texto = AIController.armarMensajeLlamada(conversacion.objetivoActual, conversacion.conversacionActual)

            conversacion.conversacionActual.append({"rol": "IA", "mensaje": texto})

            log.info(f"Se genero la siguiente respuesta: {texto}")

            elevenLabsResponse = elevenLabs.tts(texto, conversacion.idVozActual, "eleven_multilingual_v2",None, None, 0.5)  # por el momento estabilidad y velocidad en None

            idAudio = elevenLabsResponse["idAudio"]

            # ----- HILO EN PARALELO ----- #
            def editarEventoEnParalelo():
                try:
                    dataEvento = {
                        "registroEvento": {
                            "conversacion": json.dumps(conversacion.conversacionActual)
                        }
                    }
                    statusEvento = EventosController.editarEvento(conversacion.idEvento, dataEvento)
                    if statusEvento != 200:
                        log.error("No se pudo actualizar el evento en hilo paralelo")
                    else:
                        log.info("Evento actualizado correctamente en hilo paralelo")
                except Exception as e:
                    log.error(f"Error actualizando evento en hilo: {str(e)}")

            hilo = threading.Thread(target=editarEventoEnParalelo)
            hilo.start()
            # ----- HILO EN PARALELO ----- #

            from app.endpoints.apis import exponerAudio
            exponerAudio(f"{idAudio}.mp3")  # expone el archivo .mp3 a internet para que Twilio pueda reproducirlo

            log.info("Se expone el audio para que Twilio lo reproduzca")

            url = host  # localhost, ngrok o cuando se despliegue
            conversacion.urlAudioActual = f"{url}/api/audios/{idAudio}.mp3"

            log.info(f"URL audio actual: {conversacion.urlAudioActual}")

            return LlamadasController.generarAccionesEnLlamada()

        except Exception as e:
            log.error(f"Hubo un error en el procesamiento de la respuesta de la llamada: {str(e)}")
            return responseError("ERROR_AL_LLAMAR", f"Hubo un error al intentar ejecutar la llamada: {str(e)}", 500)

    @staticmethod
    def generarAccionesEnLlamada():

        response = VoiceResponse()

        response.play(conversacion.urlAudioActual)

        gather = Gather(
            input='speech',
            language="es-MX",
            action=host + '/api/twilio/respuesta',
            method='POST',
            speech_timeout='auto',
            timeout=3
        )

        response.append(gather)

        log.info(f"Lo que le mandamos a twilio es: {str(response)}")

        return Response(str(response), mimetype="application/xml")


    @staticmethod
    def validarRequestLlamada(data):
        if not data or "password" not in data:
            return responseError("CREDENCIAL_INCORRECTA", "Credencial incorrecta", 401)

        if data["password"] != password:
            return responseError("CREDENCIAL_INCORRECTA", "Credencial incorrecta", 401)

        if "idUsuarioDestinatario" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'idUsuarioDestinatario'",400)

        if "idUsuarioRemitente" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Falta el campo obligatorio 'idUsuarioRemitente'",400)

        return None

    #@staticmethod
    #def convertirConversacionAString(lista):
    #"""Convierte la conversación (lista de dicts) a un string legible para un prompt."""
    #prompt = ""

    #for msg in lista:
        #    rol = msg.get("rol", "").lower()
        #   contenido = msg.get("mensaje", "").strip()

        #  if rol == "ia":
        #       prompt += f"IA: {contenido}\n"
        #   elif rol == "destinatario":
        #       prompt += f"Usuario: {contenido}\n"

    #   return prompt

    @staticmethod
    def analizarLlamada():
        log.info(f"[ANÁLISIS] ========== INICIANDO ANÁLISIS DE LLAMADA ==========")
        log.info(f"[ANÁLISIS] Evento ID: {conversacion.idEvento}, Destinatario: {conversacion.destinatario}, Remitente: {conversacion.remitente}")
        log.info(f"[ANÁLISIS] Objetivo específico: {conversacion.objetivoEspecifico}")
        log.info(f"[ANÁLISIS] Evento desencadenador: {conversacion.eventoDesencadenador}")
        log.info(f"[ANÁLISIS] Conversación actual tiene {len(conversacion.conversacionActual)} mensajes")
        
        # Luego de los 2 minutos, la IA analiza la conversacion guardada en la variable global
        try:
            objetivo = conversacion.objetivoActual.split("Tu meta es que el empleado")[1].split("inmediatamente después")[0].strip() # Obtenemos lo que hay entre estas dos oraciones
            log.info(f"[ANÁLISIS] Objetivo extraído para análisis: '{objetivo}'")
        except Exception as e:
            log.error(f"[ANÁLISIS] Error al extraer el objetivo: {str(e)}")
            log.error(f"[ANÁLISIS] Objetivo actual completo: {conversacion.objetivoActual}")
            return
        
        log.info(f"[ANÁLISIS] Llamando a IA para analizar si se cumplió el objetivo...")
        log.info(f"[ANÁLISIS] Conversación a analizar: {json.dumps(conversacion.conversacionActual, ensure_ascii=False)}")
        
        objetivoCumplido = AIController.analizarConversacionLlamada(objetivo, conversacion.conversacionActual)
        conversacionString = LlamadasController.convertirConversacionAString(conversacion.conversacionActual)

        log.info(f"[ANÁLISIS] Resultado del análisis de IA: {'OBJETIVO CUMPLIDO' if objetivoCumplido else 'OBJETIVO NO CUMPLIDO'}")

        if objetivoCumplido:

            log.info(f"[ANÁLISIS] ✓ El objetivo de la llamada se ha cumplido (IA analizó y en la conversación se nombró el objetivo)")
            log.info(f"[ANÁLISIS] Sumando falla para destinatario {conversacion.destinatario} en evento {conversacion.idEvento}...")
            ResultadoEventoController.sumarFalla(conversacion.destinatario, conversacion.idEvento)
            log.info(f"[ANÁLISIS] Falla sumada correctamente")

            if conversacion.eventoDesencadenador.lower() == "correo":

                log.info(f"[ANÁLISIS] El evento desencadenador es un CORREO, generando email...")

                # Determinar dificultad basándose en objetivoEspecifico (igual que para mensajes)
                if conversacion.objetivoEspecifico == "Abra un link que se le enviara por":
                    dificultad = "facil"
                    contexto = f"En base a la conversación mantenida por llamada, donde el remitente tenía el rol de IA, genera un email de phishing formal dirigido al empleado de PG Control: {conversacion.nombreEmpleado} que tiene el rol de destinatario. Aquí tienes la conversación completa: {conversacionString}"
                    log.info(f"[ANÁLISIS] Dificultad determinada: FÁCIL (objetivo: abrir link)")
                elif conversacion.objetivoEspecifico == "Abra un link para ingresar sus credenciales que se le enviara por":
                    dificultad = "medio"
                    contexto = f"En base a la conversación mantenida por llamada, donde el remitente tenía el rol de IA, genera un email de phishing formal que pida el login en un formulario (como caisteLogin.html) y credenciales del empleado de la empresa PG Control: {conversacion.nombreEmpleado} que tiene el rol de destinatario. Aquí tienes la conversación completa: {conversacionString}"
                    log.info(f"[ANÁLISIS] Dificultad determinada: MEDIO (objetivo: ingresar credenciales)")
                else:
                    dificultad = "dificil"
                    contexto = f"En base a la conversación mantenida por llamada, donde el remitente tenía el rol de IA, genera un email de phishing formal que pida que el empleado de la empresa PG Control: {conversacion.nombreEmpleado} que tiene el rol de destinatario actualice urgente sus datos con enlace a caisteDatos.html. Aquí tienes la conversación completa: {conversacionString}"
                    log.info(f"[ANÁLISIS] Dificultad determinada: DIFÍCIL (objetivo por defecto)")

                nivel = 3 if dificultad == "dificil" else (2 if dificultad == "medio" else 1)
                log.info(f"[ANÁLISIS] Nivel numérico para IA: {nivel}")
                
                data = {
                    "contexto": contexto,
                    "nivel": nivel,
                    "formato": "texto"
                }
                
                log.info(f"[ANÁLISIS] Generando email con IA usando contexto y nivel {nivel}...")
                respuesta, status = AIController.armarEmail(data)

                if status != 201:
                    log.error(f"[ANÁLISIS] ✗ La IA no pudo armar el email. Status: {status}, Respuesta: {respuesta}")
                    return

                log.info(f"[ANÁLISIS] Email generado por IA exitosamente, parseando respuesta...")
                try:
                    data = json.loads(respuesta)  # convertir string a JSON real
                    log.info(f"[ANÁLISIS] Email parseado correctamente. Asunto: {data.get('asunto', 'N/A')}")
                except json.JSONDecodeError as e:
                    log.error(f"[ANÁLISIS] ✗ El texto devuelto no es JSON válido: {respuesta}, Error: {str(e)}")
                    return

                dataMail = {
                    "proveedor": "twilio",
                    "idUsuarioDestinatario": conversacion.destinatario,
                    "idUsuarioRemitente": conversacion.remitente,
                    "asunto": data["asunto"],
                    "cuerpo": data["cuerpo"],
                    "dificultad": dificultad
                }

                log.info(f"[ANÁLISIS] Enviando email usando enviarMailPorID con dificultad '{dificultad}'...")
                EmailController.enviarMailPorID(dataMail)
                log.info(f"[ANÁLISIS] ✓ Email enviado correctamente")

            else:

                log.info(f"[ANÁLISIS] El evento desencadenador es un MENSAJE ({conversacion.eventoDesencadenador}), generando mensaje...")

                if conversacion.objetivoEspecifico == "Abra un link que se le enviara por":
                    dificultad = "facil"
                    contexto = f"En base a la conversación mantenida por llamada, donde el remitente tenía el rol de IA, genera un mensaje de phishing formal para el empleado de PG Control: {conversacion.nombreEmpleado}, que tiene el rol de destinatario. Aquí tienes la conversación completa: {conversacionString}"
                    log.info(f"[ANÁLISIS] Dificultad determinada: FÁCIL (objetivo: abrir link)")
                elif conversacion.objetivoEspecifico == "Abra un link para ingresar sus credenciales que se le enviara por":
                    dificultad = "medio"
                    contexto = f"En base a la conversación mantenida por llamada, donde el remitente tenía el rol de IA, genera un mensaje de phishing formal para pedir el login en un formulario (como caisteLogin.html) y credenciales del empleado de la empresa PG Control: {conversacion.nombreEmpleado} que tiene el rol de destinatario. Aquí tienes la conversación completa: {conversacionString}"
                    log.info(f"[ANÁLISIS] Dificultad determinada: MEDIO (objetivo: ingresar credenciales)")
                else:
                    dificultad = "dificil"
                    contexto = f"En base a la conversación mantenida por llamada, donde el remitente tenía el rol de IA, genera un mensaje de phishing formal para pedir la actualización urgente de datos con enlace a caisteDatos.html para el empleado de PG Control: {conversacion.nombreEmpleado}, que tiene el rol de destinatario. Aquí tienes la conversación completa: {conversacionString}"
                    log.info(f"[ANÁLISIS] Dificultad determinada: DIFÍCIL (objetivo por defecto)")

                datamsj2 = {
                    "contexto": contexto,
                    "nivel": dificultad
                }
                
                log.info(f"[ANÁLISIS] Generando mensaje con IA usando contexto y nivel '{dificultad}'...")
                respuesta, status = AIController.armarMensaje(datamsj2)

                if status != 201:
                    log.error(f"[ANÁLISIS] ✗ La IA no pudo armar el mensaje. Status: {status}, Respuesta: {respuesta}")
                    return

                log.info(f"[ANÁLISIS] Mensaje generado por IA exitosamente")
                datamsj = {
                    "medio": conversacion.eventoDesencadenador.lower(),
                    "idUsuario": conversacion.destinatario,
                    "mensaje": respuesta["mensaje"],
                    "dificultad": dificultad
                }
                
                log.info(f"[ANÁLISIS] Enviando mensaje usando enviarMensajePorID con medio '{datamsj['medio']}' y dificultad '{dificultad}'...")
                MsjController.enviarMensajePorID(datamsj)
                log.info(f"[ANÁLISIS] ✓ Mensaje enviado correctamente")

        else:
            log.info(f"[ANÁLISIS] ✗ El objetivo de la llamada NO se ha cumplido, NO se genera ningún evento posterior")
            log.info(f"[ANÁLISIS] Sumando puntos de reportado para destinatario {conversacion.destinatario} en evento {conversacion.idEvento}...")
            ResultadoEventoController.sumarReportado(conversacion.destinatario, conversacion.idEvento)
            log.info(f"[ANÁLISIS] Puntos de reportado sumados correctamente")
        
        log.info(f"[ANÁLISIS] ========== ANÁLISIS DE LLAMADA COMPLETADO ==========")
