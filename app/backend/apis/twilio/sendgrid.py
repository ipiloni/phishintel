from app.utils.config import get
from sendgrid import SendGridAPIClient, Email
from sendgrid.helpers.mail import Mail
from app.utils.logger import log

api_key = get("SENDGRID_TOKEN_IGNA")
phishintel_api_key = get("SENDGRID_EMAILS_PHISHINTEL")
pgcontrol_api_key = get("SENDGRID_EMAILS_PGCONTROL")

def enviarMail(asunto, cuerpo, destinatario):
    from_email = Email(email='ipiloni@frba.utn.edu.ar', name='Phishintel')
    message = Mail(
        from_email=from_email,
        to_emails=destinatario,
        subject=asunto,
        html_content=cuerpo
    )
    sg = SendGridAPIClient(api_key)
    return sg.send(message)

def enviarNotificacionEmail(asunto, cuerpo, destinatario):
    from_email = Email(email='phishingintel@gmail.com', name='Administracion desde PhishIntel')
    message = Mail(
        from_email=from_email,
        to_emails=destinatario,
        subject=asunto,
        html_content=cuerpo
    )
    log.info(f"Enviando email con PhishIntel API a: {destinatario}")
    log.info(f"API Key configurada: {'Sí' if phishintel_api_key else 'No'}")
    sg = SendGridAPIClient(phishintel_api_key)
    try:
        response = sg.send(message)
        log.info(f"Email enviado exitosamente. Status: {response.status_code}")
        return response
    except Exception as e:
        log.error(f"Error enviando email con PhishIntel API: {str(e)}")
        log.error(f"Tipo de error: {type(e).__name__}")
        if hasattr(e, 'response'):
            log.error(f"Response status: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
            log.error(f"Response body: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")
        raise

def enviarMailPG(asunto, cuerpo, remitente, destinatario, name="PGControl"):
    from_email = Email(email=remitente, name=name)
    message = Mail(
        from_email=from_email,
        to_emails=destinatario,
        subject=asunto,
        html_content=cuerpo
    )
    log.info(f"Enviando email con PGControl API desde: {remitente} ({name}) a: {destinatario}")
    log.info(f"API Key configurada: {'Sí' if pgcontrol_api_key else 'No'}")
    sg = SendGridAPIClient(pgcontrol_api_key)
    try:
        response = sg.send(message)
        log.info(f"Email enviado exitosamente. Status: {response.status_code}")
        return response
    except Exception as e:
        log.error(f"Error enviando email con PGControl API: {str(e)}")
        log.error(f"Tipo de error: {type(e).__name__}")
        if hasattr(e, 'response'):
            log.error(f"Response status: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
            log.error(f"Response body: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")
        raise