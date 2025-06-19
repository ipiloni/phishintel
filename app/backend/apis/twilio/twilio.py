# Download the helper library from https://www.twilio.com/docs/python/install
import os

from flask import jsonify
from twilio.rest import Client

# Set environment variables for your credentials
# Read more at http://twil.io/secure

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