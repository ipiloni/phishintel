from flask import jsonify
from twilio.rest import Client

from app.utils.config import get
from app.utils.logger import log

account_sid = get("TWILIO_ACCOUNT_SID_MORA")
auth_token = get("TWILIO_AUTH_TOKEN_MORA")

client = Client(account_sid, auth_token)

def llamar(destinatario, remitente, url_audio):
    log.info(f"Se recibio una solicitud para llamar al destinatario {str(destinatario)}")

    call = client.calls.create(
      url=url_audio,
      to=destinatario,
      from_=remitente,
    )

    log.info(f"Resultados actuales: {call.sid} - {call.duration} - {call.status} - {call.direction}")

    return jsonify({
      'sid': call.sid,
      'status': call.status
    })