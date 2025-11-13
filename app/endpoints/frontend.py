import logging

from flask import Blueprint, send_from_directory, request, redirect, url_for, session
import os

from app.controllers.login import AuthController
from app.controllers.resultadoEventoController import ResultadoEventoController
from app.utils.url_encoder import decode_phishing_params, decode_route
from app.utils.logger import log

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
@frontend.route("/syslogin")
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
@frontend.route("/verify")
def caiste():
    """
    Ruta para verificación (dificultad fácil).
    Soporta tanto la ruta antigua (/caiste) como la nueva (/verify).
    """
    # Intentar obtener parámetros codificados primero (nueva forma)
    encoded_params = request.args.get('t')
    if encoded_params:
        decoded = decode_phishing_params(encoded_params)
        if decoded:
            idUsuario = decoded.get('idUsuario')
            idEvento = decoded.get('idEvento')
            if idUsuario and idEvento:
                ResultadoEventoController.sumarFalla(idUsuario, idEvento)
                return redirect(url_for('frontend.caiste'))
    
    # Fallback: Intentar obtener parámetros de la URL (forma antigua - compatibilidad)
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
@frontend.route("/auth")
def caisteLogin():
    """
    Ruta para login de phishing (dificultad media).
    Soporta tanto la ruta antigua (/caisteLogin) como la nueva (/auth).
    """
    # Intentar obtener parámetros codificados primero (nueva forma)
    encoded_params = request.args.get('t')
    log.info(f"[CAISTE_LOGIN] Iniciando - URL params: {dict(request.args)}, encoded_params presente: {encoded_params is not None}")
    
    if encoded_params:
        decoded = decode_phishing_params(encoded_params)
        log.info(f"[CAISTE_LOGIN] Parámetros decodificados: {decoded}")
        if decoded:
            idUsuario = decoded.get('idUsuario')
            idEvento = decoded.get('idEvento')
            log.info(f"[CAISTE_LOGIN] idUsuario: {idUsuario}, idEvento: {idEvento}")
            if idUsuario and idEvento:
                # Registrar FALLA inmediatamente al hacer clic en el link
                log.info(f"[CAISTE_LOGIN] Registrando FALLA SIMPLE - Usuario: {idUsuario}, Evento: {idEvento}")
                resultado = ResultadoEventoController.sumarFalla(idUsuario, idEvento)
                log.info(f"[CAISTE_LOGIN] Resultado de sumarFalla: {resultado}")
                # Leer el HTML y agregar campos ocultos al formulario
                html_path = os.path.join(FRONTEND_DIR, "caisteLogin.html")
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                # Agregar campos ocultos al formulario antes del botón de submit
                campos_ocultos = f'''<input type="hidden" id="caiste_idUsuario" name="caiste_idUsuario" value="{idUsuario}">
                <input type="hidden" id="caiste_idEvento" name="caiste_idEvento" value="{idEvento}">'''
                html_content = html_content.replace('<button type="submit"', campos_ocultos + '\n                <button type="submit"')
                # Limpiar la URL sin recargar la página
                script_tag = f'''<script>
                    if (window.history.replaceState) {{
                        window.history.replaceState(null, null, window.location.pathname);
                    }}
                </script>'''
                html_content = html_content.replace('</body>', script_tag + '</body>')
                from flask import Response
                return Response(html_content, mimetype='text/html')
    
    # Fallback: Intentar obtener parámetros de la URL (forma antigua - compatibilidad)
    idUsuario = request.args.get('idUsuario', type=int)
    idEvento = request.args.get('idEvento', type=int)
    log.info(f"[CAISTE_LOGIN] Fallback - idUsuario: {idUsuario}, idEvento: {idEvento}")
    
    if idUsuario and idEvento:
        # Registrar FALLA inmediatamente al hacer clic en el link
        log.info(f"[CAISTE_LOGIN] Registrando FALLA SIMPLE (fallback) - Usuario: {idUsuario}, Evento: {idEvento}")
        resultado = ResultadoEventoController.sumarFalla(idUsuario, idEvento)
        log.info(f"[CAISTE_LOGIN] Resultado de sumarFalla (fallback): {resultado}")
        # Leer el HTML y agregar campos ocultos al formulario
        html_path = os.path.join(FRONTEND_DIR, "caisteLogin.html")
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        # Agregar campos ocultos al formulario antes del botón de submit
        campos_ocultos = f'''<input type="hidden" id="caiste_idUsuario" name="caiste_idUsuario" value="{idUsuario}">
        <input type="hidden" id="caiste_idEvento" name="caiste_idEvento" value="{idEvento}">'''
        html_content = html_content.replace('<button type="submit"', campos_ocultos + '\n                <button type="submit"')
        # Limpiar la URL sin recargar la página
        script_tag = f'''<script>
            if (window.history.replaceState) {{
                window.history.replaceState(null, null, window.location.pathname);
            }}
        </script>'''
        html_content = html_content.replace('</body>', script_tag + '</body>')
        from flask import Response
        return Response(html_content, mimetype='text/html')
    
    return send_from_directory(FRONTEND_DIR, "caisteLogin.html")

@frontend.route("/caisteDatos")
@frontend.route("/update")
def caisteDatos():
    """
    Ruta para actualización de datos (dificultad difícil).
    Soporta tanto la ruta antigua (/caisteDatos) como la nueva (/update).
    """
    # Intentar obtener parámetros codificados primero (nueva forma)
    encoded_params = request.args.get('t')
    log.info(f"[CAISTE_DATOS] Iniciando - URL params: {dict(request.args)}, encoded_params presente: {encoded_params is not None}")
    
    if encoded_params:
        decoded = decode_phishing_params(encoded_params)
        log.info(f"[CAISTE_DATOS] Parámetros decodificados: {decoded}")
        if decoded:
            idUsuario = decoded.get('idUsuario')
            idEvento = decoded.get('idEvento')
            log.info(f"[CAISTE_DATOS] idUsuario: {idUsuario}, idEvento: {idEvento}")
            if idUsuario and idEvento:
                # Registrar FALLA inmediatamente al hacer clic en el link
                log.info(f"[CAISTE_DATOS] Registrando FALLA SIMPLE - Usuario: {idUsuario}, Evento: {idEvento}")
                resultado = ResultadoEventoController.sumarFalla(idUsuario, idEvento)
                log.info(f"[CAISTE_DATOS] Resultado de sumarFalla: {resultado}")
                # Leer el HTML y agregar campos ocultos al formulario
                html_path = os.path.join(FRONTEND_DIR, "caisteDatos.html")
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                # Agregar campos ocultos al formulario antes del botón de submit
                campos_ocultos = f'''<input type="hidden" id="caiste_idUsuario" name="caiste_idUsuario" value="{idUsuario}">
                <input type="hidden" id="caiste_idEvento" name="caiste_idEvento" value="{idEvento}">'''
                html_content = html_content.replace('<button type="submit"', campos_ocultos + '\n                <button type="submit"')
                # Limpiar la URL sin recargar la página
                script_tag = f'''<script>
                    if (window.history.replaceState) {{
                        window.history.replaceState(null, null, window.location.pathname);
                    }}
                </script>'''
                html_content = html_content.replace('</body>', script_tag + '</body>')
                from flask import Response
                return Response(html_content, mimetype='text/html')
    
    # Fallback: Intentar obtener parámetros de la URL (forma antigua - compatibilidad)
    idUsuario = request.args.get('idUsuario', type=int)
    idEvento = request.args.get('idEvento', type=int)
    log.info(f"[CAISTE_DATOS] Fallback - idUsuario: {idUsuario}, idEvento: {idEvento}")
    
    if idUsuario and idEvento:
        # Registrar FALLA inmediatamente al hacer clic en el link
        log.info(f"[CAISTE_DATOS] Registrando FALLA SIMPLE (fallback) - Usuario: {idUsuario}, Evento: {idEvento}")
        resultado = ResultadoEventoController.sumarFalla(idUsuario, idEvento)
        log.info(f"[CAISTE_DATOS] Resultado de sumarFalla (fallback): {resultado}")
        # Leer el HTML y agregar campos ocultos al formulario
        html_path = os.path.join(FRONTEND_DIR, "caisteDatos.html")
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        # Agregar campos ocultos al formulario antes del botón de submit
        campos_ocultos = f'''<input type="hidden" id="caiste_idUsuario" name="caiste_idUsuario" value="{idUsuario}">
        <input type="hidden" id="caiste_idEvento" name="caiste_idEvento" value="{idEvento}">'''
        html_content = html_content.replace('<button type="submit"', campos_ocultos + '\n                <button type="submit"')
        # Limpiar la URL sin recargar la página
        script_tag = f'''<script>
            if (window.history.replaceState) {{
                window.history.replaceState(null, null, window.location.pathname);
            }}
        </script>'''
        html_content = html_content.replace('</body>', script_tag + '</body>')
        from flask import Response
        return Response(html_content, mimetype='text/html')
    
    return send_from_directory(FRONTEND_DIR, "caisteDatos.html")

@frontend.route("/verificarlogin", methods=["POST"])
def verificarlogin():
    data = request.get_json()
    return AuthController.login(data)


# Ruta para cualquier otro archivo dentro de frontend (CSS, JS, imágenes, vendor, etc.)
@frontend.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)