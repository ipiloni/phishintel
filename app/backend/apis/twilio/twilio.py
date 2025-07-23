from flask import jsonify
from twilio.rest import Client

from app.utils.config import get

account_sid = get("TWILIO_ACCOUNT_SID_IGNA")
auth_token = get("TWILIO_AUTH_TOKEN_IGNA")

client = Client(account_sid, auth_token)

def llamar(destinatario, remitente):
  print(f"Llego a la llamada")

  call = client.calls.create(
    url="http://demo.twilio.com/docs/voice.xml",
    to=destinatario,
    from_=remitente,
  )
  print(f"Imprimo resultados")

  print(call.sid)
  print(call.duration)
  print(call.status)
  print(call.direction)

  return jsonify({
    'sid': call.sid,
    'status': call.status
  })