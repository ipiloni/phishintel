from app.utils.config import get
from sendgrid import SendGridAPIClient, Email
from sendgrid.helpers.mail import Mail

api_key = get("SENDGRID_TOKEN_IGNA")
phishintel_api_key = get("SENDGRID_EMAILS_PHISHINTEL")

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
    from_email = Email(email='phishingintel@gmail.com', name='PhishIntel')
    message = Mail(
        from_email=from_email,
        to_emails=destinatario,
        subject=asunto,
        html_content=cuerpo
    )
    sg = SendGridAPIClient(phishintel_api_key)
    return sg.send(message)