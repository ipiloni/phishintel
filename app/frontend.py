from flask import Blueprint, send_from_directory
import os

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
   return send_from_directory(os.path.join(frontend.root_path, "frontend"), "reportes.html")

@frontend.route("/principal")
def principal():
   return send_from_directory(os.path.join(frontend.root_path, "frontend"), "principal.html")
@frontend.route("/usuarios")
def usuarios():
   return send_from_directory(os.path.join(frontend.root_path, "frontend"), "usuarios.html")

# Ruta para cualquier otro archivo dentro de frontend (CSS, JS, imágenes, vendor, etc.)
@frontend.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(os.path.join(frontend.root_path, "frontend"), filename)