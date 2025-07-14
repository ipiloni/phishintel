from flask import jsonify
from twilio.rest import Client

client = Client("account_sid", "auth_token")

def llamar():
  print(f"Llego a la llamada")

  call = client.calls.create(
    url="http://demo.twilio.com/docs/voice.xml",
    to="+5491141635935",
    from_="+18647148760"
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