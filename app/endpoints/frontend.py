import logging

from flask import Blueprint, send_from_directory, request, redirect, url_for, session
import os

from app.controllers.login import AuthController
from app.controllers.resultadoEventoController import ResultadoEventoController

frontend = Blueprint("frontend", __name__, static_folder="frontend")

# Obtener la ruta correcta a la carpeta frontend
# __file__ está en app/endpoints/frontend.py, entonces:
# os.path.dirname(__file__) = app/endpoints/
# os.path.dirname(os.path.dirname(__file__)) = app/
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

# ------ # FRONTEND # ------ #
# Ruta para servir el index.html
# Ruta para el index
@frontend.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@frontend.route("/login")
def login():
   return send_from_directory(FRONTEND_DIR, "login.html")

@frontend.route("/registro")
def registro():
   return send_from_directory(FRONTEND_DIR, "register.html")

@frontend.route("/reportes")
def reportes():
   return send_from_directory(FRONTEND_DIR, "principalReportes.html")

@frontend.route("/abm")
def abm():
   return send_from_directory(FRONTEND_DIR, "principalABM.html")

@frontend.route("/principal")
def principal():
   return send_from_directory(FRONTEND_DIR, "principal.html")

@frontend.route("/principalEmpleado")
def principalEmpleado():
   return send_from_directory(FRONTEND_DIR, "principalEmpleado.html")

@frontend.route("/principalEmpleadoScoring")
def principalEmpleadoScoring():
   return send_from_directory(FRONTEND_DIR, "principalEmpleadoScoring.html")

@frontend.route("/principalEmpleadoReportar")
def principalEmpleadoReportar():
   return send_from_directory(FRONTEND_DIR, "principalEmpleadoReportar.html")

@frontend.route("/selectorCampania")
def selectorCampania():
   return send_from_directory(FRONTEND_DIR, "principalSelectorCampania.html")
@frontend.route("/campania-llamada")
def campaniaLlamada():
   return send_from_directory(FRONTEND_DIR, "campaniaLlamada.html")
@frontend.route("/campania-email")
def campaniaEmail():
   return send_from_directory(FRONTEND_DIR, "campaniaEmail.html")

@frontend.route("/campania-mensaje")
def campaniaMensaje():
   return send_from_directory(FRONTEND_DIR, "campaniaMensajes.html")

@frontend.route("/enConstruccion")
def enConstruccion():
   return send_from_directory(FRONTEND_DIR, "enConstruccion.html")

@frontend.route("/caiste")
def caiste():
    # Primero intentar obtener parámetros de la URL (dificultad fácil/difícil)
    idUsuario = request.args.get('idUsuario', type=int)
    idEvento = request.args.get('idEvento', type=int)
    
    # Si no hay parámetros en URL, intentar obtener de la sesión (dificultad media)
    if not idUsuario or not idEvento:
        idUsuario = session.get('caiste_idUsuario')
        idEvento = session.get('caiste_idEvento')
        # Limpiar la sesión después de usar los parámetros
        if idUsuario and idEvento:
            session.pop('caiste_idUsuario', None)
            session.pop('caiste_idEvento', None)
    
    if idUsuario and idEvento:
        ResultadoEventoController.sumarFalla(idUsuario, idEvento)
        # Redirigir a la misma ruta sin parámetros para limpiar la URL
        return redirect(url_for('frontend.caiste'))
    
    return send_from_directory(FRONTEND_DIR, "caiste.html")

@frontend.route("/caisteLogin")
def caisteLogin():
    idUsuario = request.args.get('idUsuario', type=int)
    idEvento = request.args.get('idEvento', type=int)
    
    if idUsuario and idEvento:
        # Almacenar parámetros en sesión para usar después
        session['caiste_idUsuario'] = idUsuario
        session['caiste_idEvento'] = idEvento
        # Redirigir a la misma ruta sin parámetros para limpiar la URL
        return redirect(url_for('frontend.caisteLogin'))
    
    return send_from_directory(FRONTEND_DIR, "caisteLogin.html")

@frontend.route("/caisteDatos")
def caisteDatos():
    idUsuario = request.args.get('idUsuario', type=int)
    idEvento = request.args.get('idEvento', type=int)
    
    if idUsuario and idEvento:
        # Almacenar parámetros en sesión para usar después
        session['caiste_idUsuario'] = idUsuario
        session['caiste_idEvento'] = idEvento
        # Redirigir a la misma ruta sin parámetros para limpiar la URL
        return redirect(url_for('frontend.caisteDatos'))
    
    return send_from_directory(FRONTEND_DIR, "caisteDatos.html")

@frontend.route("/verificarlogin", methods=["POST"])
def verificarlogin():
    data = request.get_json()
    return AuthController.login(data)

# Ruta para cualquier otro archivo dentro de frontend (CSS, JS, imágenes, vendor, etc.)
@frontend.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)