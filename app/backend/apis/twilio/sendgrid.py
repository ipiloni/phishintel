from app.utils.config import get
from sendgrid import SendGridAPIClient, Email
from sendgrid.helpers.mail import Mail

api_key = get("SENDGRID_TOKEN_IGNA")

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