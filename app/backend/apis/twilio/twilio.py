import os
from flask import jsonify
from twilio.rest import Client

from app.utils.logger import log

account_sid = os.environ.get("TWILIO_ACCOUNT_SID_MORA")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN_MORA")

client = Client(account_sid, auth_token)

def llamar(destinatario, remitente, url_audio):
    log.info(f"Se recibio una solicitud para llamar al destinatario {str(destinatario)}")

    call = client.calls.create(
      url=url_audio, # endpoint donde twilio obtiene la tarea que debe hacer
      to=destinatario,
      from_=remitente,
    )

    log.info(f"Resultados actuales: {call.sid} - {call.duration} - {call.status} - {call.direction}")
    import app.utils.conversacion as conversacion
    conversacion.idConversacion = call.sid

    return jsonify({
      'sid': call.sid,
      'status': call.status
    })

def obtenerEstadoLlamada(sid):
    log.info(f"Se recibio una solicitud para obtener el estado de la llamada {str(sid)}")

    call = client.calls(sid).fetch()

    log.info(f"Resultados actuales: {call.sid} - {call.duration} - {call.status} - {call.direction}")

    return jsonify({
      'sid': call.sid,
      'status': call.status
    })