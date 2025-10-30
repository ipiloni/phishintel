import datetime
import re

from flask import jsonify
from bs4 import BeautifulSoup
from app.backend.models import RegistroEvento, Usuario
from app.backend.models.error import responseError
from app.backend.models.evento import Evento
from app.backend.models.resultadoEvento import ResultadoEvento
from app.backend.models.tipoEvento import TipoEvento
from app.backend.models.usuarioxevento import UsuarioxEvento
from app.config.db_config import SessionLocal
from app.backend.apis.twilio.sendgrid import enviarMail as enviarMailTwilio, enviarNotificacionEmail, enviarMailPG
from app.backend.apis.smtp.smtpconnection import SMTPConnection
from app.controllers.aiController import AIController
from app.utils.logger import log

class EmailController:

    # =================== MÉTODOS ACTIVOS (EN USO) =================== #

    @staticmethod
    def enviarMailPorID(data):
        if not data or "proveedor" not in data or "idUsuarioDestinatario" not in data or "asunto" not in data or "cuerpo" not in data or "dificultad" not in data:
            return responseError("CAMPOS_OBLIGATORIOS",
                                 "Faltan campos obligatorios como 'proveedor', 'idUsuarioDestinatario', 'asunto', 'cuerpo' o 'dificultad'", 400)

        proveedor = data["proveedor"]
        id_usuario_destinatario = data["idUsuarioDestinatario"]
        id_usuario_remitente = data.get("idUsuarioRemitente")  # Opcional, solo para dificultad Difícil
        asunto = data["asunto"]
        cuerpo = data["cuerpo"]  # Texto plano desde el frontend
        dificultad = data["dificultad"]

        session = SessionLocal()
        try:
            # Buscar el usuario destinatario en la BD
            usuario_destinatario = session.query(Usuario).filter_by(idUsuario=id_usuario_destinatario).first()
            if not usuario_destinatario or not usuario_destinatario.correo:
                session.close()
                return responseError("USUARIO_NO_ENCONTRADO",
                                     "No se encontró el usuario destinatario o no tiene correo registrado", 404)

            # Crear el evento y registro
            # Convertir texto plano a HTML básico para envío y registro
            cuerpo_html = EmailController.text_to_html_basic(cuerpo)

            registroEvento = RegistroEvento(asunto=asunto, cuerpo=cuerpo_html)
            evento = Evento(
                tipoEvento=TipoEvento.CORREO,
                fechaEvento=datetime.datetime.now(),
                registroEvento=registroEvento
            )
            session.add(evento)
            session.commit()  # Para obtener idEvento

            # Vincular el evento con el usuario destinatario
            usuario_evento = UsuarioxEvento(
                idUsuario=id_usuario_destinatario,
                idEvento=evento.idEvento,
                resultado=ResultadoEvento.PENDIENTE
            )
            session.add(usuario_evento)
            session.commit()

            # Construir link según dificultad
            if dificultad.lower() in ["medio", "media"]:
                # Dificultad Media: Usar caisteLogin para mayor realismo
                link_caiste = f"http://localhost:8080/caisteLogin?idUsuario={id_usuario_destinatario}&idEvento={evento.idEvento}"
            elif dificultad.lower() in ["difícil", "dificil"]:
                # Dificultad Difícil: Usar caisteDatos para solicitar datos sensibles
                link_caiste = f"http://localhost:8080/caisteDatos?idUsuario={id_usuario_destinatario}&idEvento={evento.idEvento}"
            else:
                # Dificultad Fácil: Usar caiste directamente
                link_caiste = f"http://localhost:8080/caiste?idUsuario={id_usuario_destinatario}&idEvento={evento.idEvento}"
            
            boton_html = (
                f"<div style=\"margin-top:20px;text-align:center\">"
                f"<a href=\"{link_caiste}\" style=\"background-color:#4898E8;color:#ffffff;padding:12px 20px;text-decoration:none;border-radius:6px;display:inline-block;font-family:Arial,Helvetica,sans-serif\">"
                f"Ver"
                f"</a>"
                f"</div>"
            )
            cuerpo_con_boton = f"{cuerpo_html}{boton_html}"

            # Obtener información del remitente para dificultad Difícil
            usuario_remitente = None
            if dificultad.lower() in ["difícil", "dificil"]:
                if not id_usuario_remitente:
                    session.rollback()
                    return responseError("REMITENTE_REQUERIDO", "Se requiere idUsuarioRemitente para dificultad Difícil", 400)
                
                usuario_remitente = session.query(Usuario).filter_by(idUsuario=id_usuario_remitente).first()
                if not usuario_remitente or not usuario_remitente.correo:
                    session.rollback()
                    return responseError("REMITENTE_NO_ENCONTRADO", "No se encontró el usuario remitente o no tiene correo registrado", 404)

            # Enviar email según dificultad
            if dificultad.lower() in ["fácil", "facil"]:
                # Dificultad Fácil: Siempre usa PhishIntel (ignora proveedor)
                # TODO: Hardcoded - destinatario debe ser configurable
                log.info(f"Enviando email con dificultad '{dificultad}' usando PhishIntel API")
                response = enviarMailPG(asunto, cuerpo_con_boton, "phishingintel@gmail.com","phishingintel@gmail.com", name="Juan Perez de PG Control")
                log.info(f"Respuesta del servicio Twilio sendgrid (PhishIntel): {response.status_code}")
                
            elif dificultad.lower() in ["medio", "media"]:
                # Dificultad Media: Usa proveedor (twilio o smtp)
                if proveedor == "twilio":
                    # TODO: Hardcoded - remitente y destinatario deben ser configurables
                    log.info(f"Enviando email con dificultad '{dificultad}' usando PGControl API (Twilio)")
                    response = enviarMailPG(asunto, cuerpo_con_boton, "administracion@pgcontrol.lat", "phishingintel@gmail.com", name="Juan Perez de PG Control")
                    log.info(f"Respuesta del servicio Twilio sendgrid (Administracion PGControl): {response.status_code}")
                elif proveedor == "smtp":
                    # TODO: Hardcoded - configuración SMTP debe ser configurable
                    from app.utils.config import get
                    smtp_host = get("SMTP_MEDIO_HOST")
                    smtp_port = get("SMTP_MEDIO_PORT")
                    smtp_user = get("SMTP_MEDIO_USER")
                    smtp_password = get("SMTP_MEDIO_PASSWORD")
                    
                    log.info(f"Enviando email con dificultad '{dificultad}' usando SMTP PrivateEmail desde '{smtp_user}'")
                    smtp = SMTPConnection(smtp_host, smtp_port)
                    smtp.login(smtp_user, smtp_password)

                    message = smtp.compose_message(
                        sender=smtp_user,
                        name="Administracion de PG Control",
                        recipients=["phishingintel@gmail.com"],
                        subject=asunto,
                        html=cuerpo_con_boton
                    )
                    smtp.send_mail(message)
                else:
                    session.rollback()
                    return responseError("PROVEEDOR_INVALIDO", "Proveedor de correo no reconocido para dificultad media", 400)
                
            elif dificultad.lower() in ["difícil", "dificil"]:
                # Dificultad Difícil: Usa proveedor (twilio o smtp) con remitente configurable
                if proveedor == "twilio":
                    # Usar email y nombre del remitente seleccionado
                    nombre_remitente = f"{usuario_remitente.nombre} {usuario_remitente.apellido} de PG Control"
                    log.info(f"Enviando email con dificultad '{dificultad}' usando Twilio desde '{usuario_remitente.correo}'")
                    response = enviarMailPG(asunto, cuerpo_con_boton, usuario_remitente.correo, "phishingintel@gmail.com", name=nombre_remitente)
                    log.info(f"Respuesta del servicio Twilio sendgrid: {response.status_code}")
                elif proveedor == "smtp":
                    # Mapeo fijo de credenciales basado en email del remitente
                    from app.utils.config import get
                    
                    if usuario_remitente.correo == "juan.perez@pgcontrol.com.ar":
                        smtp_host = get("SMTP_DIFICIL_HOST")
                        smtp_port = get("SMTP_DIFICIL_PORT")
                        smtp_user = get("SMTP_DIFICIL_USER")
                        smtp_password = get("SMTP_DIFICIL_PASSWORD")
                    elif usuario_remitente.correo == "marcos.gurruchaga@pgcontrol.com.ar":
                        smtp_host = get("SMTP_DIFICIL_HOST")
                        smtp_port = get("SMTP_DIFICIL_PORT")
                        smtp_user = get("SMTP_DIFICIL_MARCOS_USER")
                        smtp_password = get("SMTP_DIFICIL_MARCOS_PASSWORD")
                    elif usuario_remitente.correo == "mora.rodriguez@pgcontrol.com.ar":
                        smtp_host = get("SMTP_DIFICIL_HOST")
                        smtp_port = get("SMTP_DIFICIL_PORT")
                        smtp_user = get("SMTP_DIFICIL_MORA_USER")
                        smtp_password = get("SMTP_DIFICIL_MORA_PASSWORD")
                    else:
                        session.rollback()
                        return responseError("REMITENTE_NO_CONFIGURADO", f"Email del remitente '{usuario_remitente.correo}' no está configurado para SMTP", 400)
                    
                    nombre_remitente = f"{usuario_remitente.nombre} {usuario_remitente.apellido}"
                    log.info(f"Enviando email con dificultad '{dificultad}' usando SMTP desde '{usuario_remitente.correo}'")
                    smtp = SMTPConnection(smtp_host, smtp_port)
                    smtp.login(smtp_user, smtp_password)
                    message = smtp.compose_message(
                        sender=usuario_remitente.correo,
                        name=nombre_remitente,
                        recipients=["phishingintel@gmail.com"],
                        subject=asunto,
                        html=cuerpo_con_boton
                    )
                    smtp.send_mail(message)
                else:
                    session.rollback()
                    return responseError("PROVEEDOR_INVALIDO", "Proveedor de correo no reconocido para dificultad difícil", 400)
            else:
                session.rollback()
                return responseError("DIFICULTAD_INVALIDA", "Dificultad no reconocida", 400)

            idnuevo = evento.idEvento
            session.close()
            return jsonify({"mensaje": "Email enviado correctamente", "idEvento": idnuevo}), 201

        except Exception as e:
            log.error(f"Error en enviarMailPorID: {str(e)}")
            log.error(f"Tipo de error: {type(e).__name__}")
            if hasattr(e, 'response'):
                log.error(f"Response status: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
                log.error(f"Response body: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")
            session.rollback()
            session.close()
            return responseError("ERROR", f"Hubo un error al enviar mail: {str(e)}", 500)

    ## Este metodo envia notificaciones de recuperar contrasenia, doble factor, etc. Es desde el email de Phishintel!
    # deberia recibir el tipo de notificacion y, en base a este, definir que asunto y cuerpo enviar, estos deberian almacenarse en la bdd porque siempre van a ser iguales
    @staticmethod
    def enviarNotificacionPhishintel(data):
        if not data or "destinatario" not in data or "asunto" not in data or "cuerpo" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios como 'destinatario', 'asunto', 'cuerpo' o 'proveedor'", 400)

        destinatario = data["destinatario"]
        asunto = data["asunto"]
        cuerpo = data["cuerpo"]

        try:
            response = enviarNotificacionEmail(asunto, cuerpo, destinatario)
            log.info(f"Respuesta del servicio Twilio sendgrid: {response.status_code}")
            return jsonify({"mensaje": "Email encolado correctamente. No se asegura recepción correcta."}), 201
        except Exception as e:
            log.error(f"Hubo un error al intentar enviar la notificacion: {str(e)}")
            return responseError("ERROR", f"Hubo un error al intentar enviar la notificacion: {str(e)}", 500)

    # =================== MÉTODOS LEGACY (NO EN USO) =================== #

    @staticmethod
    def enviarMail(data):
        if not data or "destinatario" not in data or "asunto" not in data or "cuerpo" not in data or "proveedor" not in data:
            return responseError("CAMPOS_OBLIGATORIOS", "Faltan campos obligatorios como 'destinatario', 'asunto', 'cuerpo' o 'proveedor'", 400)

        destinatario = data["destinatario"]
        asunto = data["asunto"]
        cuerpo = data["cuerpo"]
        proveedor = data["proveedor"]  # "twilio" o "smtp"

        try:
            # Guardar evento y registro en DB
            registroEvento:RegistroEvento = RegistroEvento(asunto=asunto, cuerpo=cuerpo)
            evento = Evento(
                tipoEvento=TipoEvento.CORREO,
                fechaEvento=datetime.datetime.now(),
                registroEvento=registroEvento
            )

            session = SessionLocal()
            session.add(evento)
            session.commit()

            # Envío del mail según proveedor
            if proveedor == "twilio":
                response = enviarMailTwilio(asunto, cuerpo, destinatario)
                log.info(f"Respuesta del servicio Twilio sendgrid: {response.status_code}")
            elif proveedor == "smtp":
                smtp = SMTPConnection("mail.pgcontrol.com.ar", "26")
                smtp.login("juan.perez@pgcontrol.com.ar", "juan.perez1")
                message = smtp.compose_message(
                    sender="juan.perez@pgcontrol.com.ar",
                    name="Administracion PG Control",
                    recipients=[destinatario],
                    subject=asunto,
                    html=cuerpo
                )
                smtp.send_mail(message)
            else:
                session.rollback()
                return responseError("PROVEEDOR_INVALIDO", "Proveedor de correo no reconocido", 400)

            session.close()
            return jsonify({"mensaje": "Email enviado correctamente"}), 201

        except Exception as e:
            log.error(f"Hubo un error al intentar enviar el email: {str(e)}")
            session.rollback()
            session.close()
            return responseError("ERROR", f"Hubo un error al enviar mail: {str(e)}", 500)

    @staticmethod
    def generarYEnviarMail(data):
        if not data or "proveedor" not in data or "idUsuario" not in data or "remitente" not in data:
            return responseError("CAMPOS_OBLIGATORIOS",
                                 "Faltan campos obligatorios como 'proveedor', 'idUsuario' o 'remitente'", 400)

        proveedor = data["proveedor"]
        id_usuario = data["idUsuario"]
        remitente = data["remitente"]

        session = SessionLocal()
        try:
            # Buscar el usuario para obtener su email
            usuario = session.query(Usuario).filter_by(idUsuario=id_usuario).first()
            if not usuario or not usuario.correo:
                session.close()
                return responseError("USUARIO_NO_ENCONTRADO", "No se encontró el usuario o no tiene correo registrado",
                                     404)

            # Creamos el evento
            registroEvento = RegistroEvento()
            evento = Evento(
                tipoEvento=TipoEvento.CORREO,
                fechaEvento=datetime.datetime.now(),
                registroEvento=registroEvento
            )
            session.add(evento)
            session.commit()  # Para obtener idEvento

            # Creamos registro en usuariosxeventos
            usuario_evento = UsuarioxEvento(
                idUsuario=id_usuario,
                idEvento=evento.idEvento,
                resultado=ResultadoEvento.PENDIENTE
            )
            session.add(usuario_evento)
            session.commit()

            # Contexto para IA con enlace personalizado
            link_falla = f"http://localhost:8080/api/sumar-falla?idUsuario={id_usuario}&idEvento={evento.idEvento}"
            contexto = (
                "Armame un email del estilo Phishing avisando que hay una compra no reconocida. "
                f"El cuerpo debe ser HTML con un botón 'Haz clic aquí' que apunte a '{link_falla}'. "
                "Devuelve en formato JSON con las claves 'asunto' y 'cuerpo'."
            )

            # Llamada a Gemini
            texto_generado, _ = AIController.armarEmail({"contexto": contexto})

            import json
            try:
                email_generado = json.loads(texto_generado)
                asunto = email_generado.get("asunto")
                cuerpo = email_generado.get("cuerpo")
            except Exception:
                session.rollback()
                session.close()
                return responseError("ERROR_JSON",
                                     "La respuesta de Gemini no es un JSON válido con 'asunto' y 'cuerpo'", 500)

            # Guardar asunto y cuerpo en registroEvento
            registroEvento.asunto = asunto
            registroEvento.cuerpo = cuerpo
            session.commit()

            # Enviar el email
            if proveedor == "twilio":

                response = enviarMailTwilio(asunto, cuerpo, usuario.correo)
                log.success(f"Twilio sendgrid response: {response.status_code}")
            elif proveedor == "smtp":
                smtp = SMTPConnection("mail.pgcontrol.com.ar", "26")
                smtp.login("juan.perez@pgcontrol.com.ar", "juan.perez1")
                message = smtp.compose_message(
                    sender=remitente,
                    name="Administración PGControl",
                    recipients=[usuario.correo],
                    subject=asunto,
                    html=cuerpo
                )
                smtp.send_mail(message)
            else:
                session.rollback()
                return responseError("PROVEEDOR_INVALIDO", "Proveedor de correo no reconocido", 400)

            idnuevo = evento.idEvento
            session.close()
            return jsonify({"mensaje": "Email generado y enviado correctamente", "idEvento": idnuevo}), 201

        except Exception as e:
            session.rollback()
            session.close()
            return responseError("ERROR", f"Hubo un error al generar y enviar el mail: {str(e)}", 500)


    # =================== UTILIDADES =================== #
    @staticmethod
    def html_to_plain_text(html: str) -> str:
        """Convierte HTML a texto plano legible para edición.
        - Quita <style> y <script>
        - Convierte <br> en \n
        - Inserta saltos de línea alrededor de elementos de bloque
        - Colapsa múltiples saltos de línea consecutivos
        """
        try:
            soup = BeautifulSoup(html or "", "html.parser")
            # Remover estilos y scripts
            for tag in soup(["style", "script"]):
                tag.decompose()

            # Reemplazar <br> por saltos de línea
            for br in soup.find_all("br"):
                br.replace_with("\n")

            # Elementos de bloque comunes → añadir separadores de línea
            block_tags = [
                "p", "div", "li", "ul", "ol",
                "h1", "h2", "h3", "h4", "h5", "h6",
                "section", "article", "header", "footer",
                "table", "thead", "tbody", "tr", "td", "th"
            ]
            for block in soup.find_all(block_tags):
                block.insert_before("\n")
                block.insert_after("\n")

            # Obtener texto y limpiar espacios
            text = soup.get_text()
            # Limpiar espacios de cada línea
            lines = [line.strip() for line in text.splitlines()]
            text = "\n".join(lines)
            # Colapsar más de 2 \n a 2
            text = re.sub(r"\n{3,}", "\n\n", text)
            # Colapsar espacios múltiples dentro de líneas largas manteniendo saltos
            text = "\n".join(re.sub(r"\s{2,}", " ", ln) for ln in text.split("\n"))
            return text.strip()
        except Exception:
            # En caso de fallo, retornar texto simple sin procesamiento adicional
            return (html or "").strip()

    @staticmethod
    def text_to_html_basic(text: str) -> str:
        """Convierte texto plano a HTML simple: párrafos y <br>."""
        if text is None:
            return ""
        try:
            # Normalizar fin de línea
            norm = text.replace("\r\n", "\n").replace("\r", "\n")
            # Separar por párrafos (doble salto)
            parts = [p.strip() for p in norm.split("\n\n")]
            parts = [p for p in parts if p]
            # Reemplazar saltos simples por <br> dentro de cada párrafo
            html_parts = [f"<p>{p.replace('\n', '<br>')}</p>" for p in parts]
            return "".join(html_parts) if html_parts else f"<p>{norm.replace('\n', '<br>')}</p>"
        except Exception:
            return f"<p>{(text or '').strip()}</p>"
