from flask import Blueprint, send_from_directory, request
import os

from app.controllers.login import AuthController

frontend = Blueprint("frontend", __name__, static_folder="frontend")

# ------ # FRONTEND # ------ #
# Ruta para servir el index.html
# Ruta para el index
@frontend.route("/")
def index():
    return send_from_directory(os.path.join(frontend.root_path, "frontend"), "index.html")

@frontend.route("/login")
def login():
   return send_from_directory(os.path.join(frontend.root_path, "frontend"), "login.html")

@frontend.route("/registro")
def registro():
   return send_from_directory(os.path.join(frontend.root_path, "frontend"), "register.html")

@frontend.route("/reportes")
def reportes():
   return send_from_directory(os.path.join(frontend.root_path, "frontend"), "principalReportes.html")

@frontend.route("/abm")
def abm():
   return send_from_directory(os.path.join(frontend.root_path, "frontend"), "principalABM.html")

@frontend.route("/principal")
def principal():
   return send_from_directory(os.path.join(frontend.root_path, "frontend"), "principal.html")
@frontend.route("/usuarios")
def usuarios():
   return send_from_directory(os.path.join(frontend.root_path, "frontend"), "usuarios.html")

@frontend.route("/selectorCampania")
def selectorCampania():
   return send_from_directory(os.path.join(frontend.root_path, "frontend"), "principalSelectorCampania.html")
@frontend.route("/campania-llamada")
def campaniaLlamada():
   return send_from_directory(os.path.join(frontend.root_path, "frontend"), "campaniaLlamada.html")
@frontend.route("/campania-email")
def campaniaEmail():
   return send_from_directory(os.path.join(frontend.root_path, "frontend"), "campaniaEmail.html")

@frontend.route("/campania-mensaje")
def campaniaMensaje():
   return send_from_directory(os.path.join(frontend.root_path, "frontend"), "campaniaMensajes.html")

@frontend.route("/enConstruccion")
def enConstruccion():
   return send_from_directory(os.path.join(frontend.root_path, "frontend"), "enConstruccion.html")

@frontend.route("/caiste")
def caiste():
   return send_from_directory(os.path.join(frontend.root_path, "frontend"), "caiste.html")
@frontend.route("/verificarlogin", methods=["POST"])
def verificarlogin():
    data = request.get_json()
    return AuthController.login(data)

# Ruta para cualquier otro archivo dentro de frontend (CSS, JS, imágenes, vendor, etc.)
@frontend.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(os.path.join(frontend.root_path, "frontend"), filename)