import json
from datetime import datetime

from flask import Response
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
host = get("URL_APP")
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

        # Elimino de la variable global la conversacion anterior
        conversacion.conversacionActual.clear()

        nombreRemitente = remitente["nombre"] + " " + remitente["apellido"]
        nombreEmpleado = usuario["nombre"] + " " + usuario["apellido"]

        rolAImitar = data["rolAImitar"]
        objetivoEspecifico = data["objetivoEspecifico"]
        eventoDesencadenador = data["eventoDesencadenador"]
        conversacion.eventoDesencadenador = eventoDesencadenador

        conversacion.objetivoActual = f"""
            Tienes el rol de {rolAImitar} dentro de la empresa 'PG Control'. Te llamas '{nombreRemitente}'.
            Tu objetivo es simular un intento de phishing telefónico, como parte de un entrenamiento de seguridad.
            Debes hablar de manera convincente, pero sin agresividad, intentando que el empleado {objetivoEspecifico} {eventoDesencadenador}.

            Reglas:
            - Si la conversación esta vacía, pues comienza con un saludo. Espera a la respuesta del empleado.
            - No uses amenazas extremas, solo urgencia laboral.
            - Responde **solo con una frase corta** que la persona diría en esta interacción. No digas nada de más ni avances la conversación.
            - En ningún momento digas que es un entrenamiento: eso se evalúa después.
            - Mantén la coherencia del rol de “{rolAImitar}”.
            - Solamente responde lo que el {rolAImitar} debería decir.
            - Eres de Buenos Aires, Argentina. Por lo que el dialecto es muy importante que lo mantengas.
            - El empleado se llama {nombreEmpleado}, trabaja en 'PG Control' en el area de {area["nombreArea"]}
        """

        log.info(f"La Conversacion actual es la siguiente: {conversacion.conversacionActual}")

        texto = AIController.armarMensajeLlamada(conversacion.objetivoActual, conversacion.conversacionActual)

        log.info(f"La IA genero el texto: {texto}")

        conversacion.conversacionActual.append({"rol": "IA", "mensaje": texto})

        dataEvento = {
            "tipoEvento": TipoEvento.LLAMADA,
            "registroEvento": {
                "objetivo": " ".join(conversacion.objetivoActual.split()).strip(),  # elimina doble espacios y \n
                "conversacion": json.dumps(conversacion.conversacionActual) # convierte la lista conversacionActual a un string para que pueda guardarse
            }
        }

        log.info(f"{dataEvento}")

        responseEvento, statusResponse = EventosController.crearEvento(dataEvento)

        if statusResponse != 201:
            log.error(f"Hubo un error al crear el evento: {responseEvento}")
            return responseEvento, statusResponse

        conversacion.idEvento = responseEvento["idEvento"]

        log.info("Evento creado correctamente, creamos el Usuario por Evento")

        responseUsuarioEvento, statusUsuarioEvento = EventosController.asociarUsuarioEvento(conversacion.idEvento, idUsuarioDestinatario, "PENDIENTE")

        if statusUsuarioEvento != 200:
            log.error(f"Hubo un error al asociar el usuario al evento: {responseUsuarioEvento}")
            return responseUsuarioEvento, statusUsuarioEvento

        log.info(f"Ahora la conversacion actual es la siguiente: {conversacion.conversacionActual}")

        conversacion.idVozActual = data.get(remitente["idVoz"], "O1CnH2NGEehfL1nmYACp")  # esto es un get o default, intenta obtener la voz del remitente y si no lo pasaron toma el default

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

        # Iniciar el hilo que analiza la llamada
        hilo = threading.Thread(target=LlamadasController.analizarLlamada)
        hilo.daemon = True  # el hilo no bloquea el cierre del programa
        hilo.start()

        return twilio.llamar(destinatario, remitente, host + "/api/twilio/accion")


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

    @staticmethod
    def analizarLlamada():
        import time
        if conversacion.hilo:
            log.info("Empieza el analisis de la llamada para detectar si se cumplio el objetivo")
            # Iniciar el hilo contador por 3 minutos
            time.sleep(180)

            # Luego de los 3 minutos, la IA analiza la conversacion guardada en la variable global
            objetivo = conversacion.objetivoActual.split("intentando que el empleado")[1].split("Reglas:")[0].strip() # Obtenemos lo que hay entre estas dos oraciones
            objetivoCumplido = AIController.analizarConversacionLlamada(objetivo, conversacion.conversacionActual)

            if objetivoCumplido:

                log.info("El objetivo de la llamada se ha cumplido (IA analizó y en la conversación se nombro el objetivo), generando evento...")
                ResultadoEventoController.sumarFalla(conversacion.destinatario, conversacion.idEvento)

                if conversacion.eventoDesencadenador.lower() == "correo":

                    log.info("El evento desencadenador es un corrreo, generando email...")

                    contexto = "Se pedirá actualización urgente de datos con enlace a caisteDatos.html. Empresa: PG Control. Sin placeholders. No incluyas enlaces; indica que el enlace se adjuntará a continuación."
                    data = {
                        "contexto": contexto,
                        "nivel": 3,
                        "formato": "texto"
                    }
                    respuesta, status = AIController.armarEmail(data)

                    if status != 201:
                        log.error(f"La IA no pudo armar el email: {respuesta}")
                        return

                    try:
                        data = json.loads(respuesta)  # convertir string a JSON real
                    except json.JSONDecodeError:
                        log.error(f"El texto devuelto no es JSON válido: {respuesta}")

                    dataMail = {
                        "proveedor": "twilio",
                        "idUsuarioDestinatario": conversacion.destinatario,
                        "idUsuarioRemitente": conversacion.remitente,
                        "asunto": data["asunto"],
                        "cuerpo": data["cuerpo"],
                        "dificultad": "dificil"
                    }

                    EmailController.enviarMailPorID(dataMail)

                else:

                    log.info(f"El evento desencadenador es un mensaje, generando email...")

                    if conversacion.objetivoEspecifico == "Abra un link que se le enviara por":
                        dificultad = "facil"
                        contexto = "Genera un mensaje de phishing formal para empleados de PG Control, contexto variable, sin marcadores como [Nombre de la empresa], no incluyas ningún enlace; indica que el enlace se adjuntará a continuación."
                    elif conversacion.objetivoEspecifico == "Abra un link para ingresar sus credenciales que se le enviara por":
                        dificultad = "medio"
                        contexto = "Se pedirá login en un formulario (como caisteLogin.html) y credenciales. Empresa: PG Control. Sin placeholders. No incluyas enlaces; indica que el enlace se adjuntará a continuación."
                    else:
                        dificultad = "dificil"
                        contexto = "Se pedirá actualización urgente de datos con enlace a caisteDatos.html. Empresa: PG Control. Sin placeholders. No incluyas enlaces; indica que el enlace se adjuntará a continuación."

                    datamsj2 = {
                        "contexto": contexto,
                        "nivel": dificultad
                    }
                    respuesta, status = AIController.armarMensaje(datamsj2)

                    if status != 201:
                        log.error(f"La IA no pudo armar el mensaje: {respuesta}")
                        return

                    datamsj = {
                        "medio": conversacion.eventoDesencadenador.lower(),
                        "idUsuario": conversacion.destinatario,
                        "mensaje": respuesta["mensaje"],
                        "dificultad": dificultad
                    }
                    MsjController.enviarMensajePorID(datamsj)

            else:
                log.info("El objetivo de la llamada NO se ha cumplido, NO se genera ningun evento pero suma puntos")
                ResultadoEventoController.sumarReportado(conversacion.destinatario, conversacion.idEvento)