from app.utils.config import get
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

api_key = get("SENDGRID_TOKEN_IGNA")

def enviarMail(asunto, cuerpo, destinatario):
    message = Mail(
        from_email='ipiloni@frba.utn.edu.ar',
        to_emails=destinatario,
        subject=asunto,
        plain_text_content=cuerpo
    )
    sg = SendGridAPIClient(api_key)
    return sg.send(message)