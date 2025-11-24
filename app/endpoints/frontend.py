from flask import Blueprint, send_from_directory, request, redirect, url_for, session
import os

from app.controllers.login import AuthController
from app.controllers.resultadoEventoController import ResultadoEventoController
from app.utils.url_encoder import decode_phishing_params
from app.utils.logger import log

frontend = Blueprint("frontend", __name__, static_folder="frontend")

# Obtener la ruta correcta a la carpeta frontend
# __file__ está en app/endpoints/frontend.py, entonces:
# os.path.dirname(__file__) = app/endpoints/
# os.path.dirname(os.path.dirname(__file__)) = app/
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

def _es_bot(user_agent, referer='', request_obj=None):
    """
    Detecta si un User-Agent pertenece a un bot/crawler/link preview.
    Incluye detección específica para link previews de SMS en Android.
    
    Args:
        user_agent (str): User-Agent string del request
        referer (str): Referer header del request (opcional)
        request_obj: Objeto request de Flask para acceder a todos los headers (opcional)
        
    Returns:
        bool: True si es un bot, False si es un navegador legítimo
    """
    if not user_agent:
        return False
    
    user_agent_lower = user_agent.lower()
    referer_lower = referer.lower() if referer else ''
    
    # Logging detallado para debugging (solo para casos sospechosos)
    debug_log = False
    
    # Lista de User-Agents conocidos de bots/crawlers/link previews
    bot_indicators = [
        'bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python-requests',
        'go-http-client', 'java/', 'okhttp', 'apache-httpclient', 'httpclient',
        'facebookexternalhit', 'twitterbot', 'linkedinbot', 'slackbot',
        'whatsapp', 'telegram', 'discordbot', 'skypebot', 'viberbot',
        'textbee', 'linkpreview', 'preview', 'fetch', 'axios', 'node-fetch',
        'postman', 'insomnia', 'httpie', 'rest-client', 'urllib',
        # User-Agents específicos para link previews de SMS en Android
        'googlebot', 'google-inspectiontool', 'google page speed',
        # Google PageRenderer - servicio de Google para generar previews/snippets
        'google-pagerenderer', 'google (+https://developers.google.com',
        # Google Messages link preview
        'messages.google.com', 'google messages',
        # Otros servicios de preview
        'linkpreview.net', 'preview.link', 'link-preview'
    ]
    
    # Detección específica para Android link previews de SMS
    # ESTRATEGIA AGRESIVA: Android WebView (wv)) es usado principalmente por apps para previews
    # Solo permitir si tiene headers muy específicos de navegador completo
    if 'android' in user_agent_lower and 'wv)' in user_agent_lower:
        debug_log = True
        # Android WebView - asumir preview a menos que tenga evidencia clara de navegador completo
        if request_obj:
            # Verificar múltiples headers para confirmar navegador completo
            accept = request_obj.headers.get('Accept', '').lower()
            accept_language = request_obj.headers.get('Accept-Language', '').lower()
            sec_fetch_site = request_obj.headers.get('Sec-Fetch-Site', '').lower()
            sec_fetch_mode = request_obj.headers.get('Sec-Fetch-Mode', '').lower()
            sec_fetch_user = request_obj.headers.get('Sec-Fetch-User', '').lower()
            sec_ch_ua = request_obj.headers.get('Sec-CH-UA', '')
            
            # Contar indicadores de navegador completo
            navegador_indicators = 0
            
            # Debe tener Accept completo con text/html
            if accept and 'text/html' in accept and ('*/*' in accept or 'application/xhtml+xml' in accept):
                navegador_indicators += 1
            
            # Debe tener Accept-Language razonable
            if accept_language and len(accept_language) >= 5:
                navegador_indicators += 1
            
            # Debe tener headers Sec-Fetch (navegadores modernos)
            if sec_fetch_site or sec_fetch_mode:
                navegador_indicators += 1
            
            # Sec-Fetch-User: ?1 indica interacción del usuario
            if sec_fetch_user == '?1':
                navegador_indicators += 1
            
            # Sec-CH-UA indica navegador Chrome moderno
            if sec_ch_ua:
                navegador_indicators += 1
            
            # Si tiene menos de 3 indicadores, probablemente es preview
            if navegador_indicators < 3:
                log.warning(f"[_es_bot] 🔍 Bloqueado: Android WebView con menos de 3 indicadores de navegador - User-Agent: {user_agent}, Indicadores: {navegador_indicators}")
                return True
        else:
            # Sin request_obj, asumir preview para WebView
            log.warning(f"[_es_bot] 🔍 Bloqueado: Android WebView sin request_obj - User-Agent: {user_agent}")
            return True
    
    # Si contiene indicadores específicos de preview
    if 'android' in user_agent_lower:
        if any(indicator in user_agent_lower for indicator in ['preview', 'linkpreview']):
            log.warning(f"[_es_bot] 🔍 Bloqueado: Indicadores de preview en Android User-Agent - User-Agent: {user_agent}")
            return True
    
    # Verificar referrer para detectar previews de apps de mensajes
    # IMPORTANTE: Si es un navegador legítimo con headers completos, NO bloquear aunque tenga referrer de messages.google.com
    # El referrer de messages.google.com puede venir cuando un usuario REAL hace clic desde la web de Google Messages
    if referer_lower:
        # Verificar si es un navegador legítimo con headers completos
        es_navegador_legitimo = False
        if request_obj:
            sec_fetch_user = request_obj.headers.get('Sec-Fetch-User', '').lower()
            sec_fetch_site = request_obj.headers.get('Sec-Fetch-Site', '').lower()
            sec_fetch_mode = request_obj.headers.get('Sec-Fetch-Mode', '').lower()
            sec_ch_ua = request_obj.headers.get('Sec-CH-UA', '')
            accept = request_obj.headers.get('Accept', '').lower()
            
            # Si tiene Sec-Fetch-User: ?1 (interacción del usuario) y otros headers de navegador completo
            # es muy probable que sea un usuario real haciendo clic
            if sec_fetch_user == '?1' and sec_fetch_site and sec_fetch_mode and accept and 'text/html' in accept:
                es_navegador_legitimo = True
            # También verificar si tiene Sec-CH-UA (Chrome moderno) y headers completos
            elif sec_ch_ua and sec_fetch_site and accept and 'text/html' in accept:
                es_navegador_legitimo = True
        
        # Solo bloquear referrer de messages.google.com si NO es un navegador legítimo con headers completos
        if 'messages.google.com' in referer_lower:
            if not es_navegador_legitimo:
                log.warning(f"[_es_bot] 🔍 Bloqueado: Referrer de messages.google.com sin headers de navegador completo - Referer: {referer}, User-Agent: {user_agent}")
                return True
            else:
                log.info(f"[_es_bot] ✅ Permitido: Referrer de messages.google.com pero navegador legítimo detectado - Referer: {referer}, User-Agent: {user_agent}")
        
        # Protocolos SMS/MMS (sms:// o mms://) - estos siempre son previews automáticos
        if referer_lower.startswith('sms://') or referer_lower.startswith('mms://'):
            log.warning(f"[_es_bot] 🔍 Bloqueado: Referrer de protocolo SMS/MMS - Referer: {referer}, User-Agent: {user_agent}")
            return True
    
    # Verificar headers adicionales para detectar previews de apps de mensajes
    if request_obj:
        # Verificar si hay headers específicos de apps de mensajes
        x_requested_with = request_obj.headers.get('X-Requested-With', '').lower()
        # Solo bloquear si es específicamente de apps de mensajes
        if x_requested_with and ('com.google.android.apps.messaging' in x_requested_with or 
                                 'android.mms' in x_requested_with or 
                                 'android.sms' in x_requested_with):
            log.warning(f"[_es_bot] 🔍 Bloqueado: X-Requested-With de app de mensajes - X-Requested-With: {x_requested_with}, User-Agent: {user_agent}")
            return True
    
    # Verificar indicadores de bot en el User-Agent
    # Esta es la verificación principal - solo retornar True si hay indicadores claros de bot
    tiene_indicadores_bot = any(indicator in user_agent_lower for indicator in bot_indicators)
    
    # Si tiene indicadores de bot, verificar headers adicionales para confirmar
    if tiene_indicadores_bot and request_obj:
        # Verificar Accept header - los previews suelen tener headers más limitados
        accept = request_obj.headers.get('Accept', '').lower()
        # Solo marcar como bot si NO acepta HTML Y tiene indicadores de bot en User-Agent
        if accept and 'text/html' not in accept:
            if debug_log:
                log.warning(f"[_es_bot] Detectado como bot por Accept header sin text/html - User-Agent: {user_agent}, Accept: {accept}")
            return True
    
    # Determinar resultado final
    # Retornar True si tiene indicadores de bot en el User-Agent
    # Las otras verificaciones (Android WebView, referrer, X-Requested-With) ya retornaron True arriba si aplicaban
    resultado = tiene_indicadores_bot
    
    # Logging detallado cuando se detecta como bot para debugging
    if resultado:
        if tiene_indicadores_bot:
            indicadores_encontrados = [ind for ind in bot_indicators if ind in user_agent_lower]
            log.warning(f"[_es_bot] 🔍 Detectado como bot por indicadores en User-Agent - Indicadores: {indicadores_encontrados}, User-Agent: {user_agent}")
        else:
            # Fue bloqueado por otra razón (WebView, referrer, etc.) pero no tiene indicadores de bot en User-Agent
            # Esto podría ser un falso positivo para navegadores legítimos
            if 'chrome' in user_agent_lower or 'firefox' in user_agent_lower or 'safari' in user_agent_lower:
                log.error(f"[_es_bot] ⚠️ POSIBLE FALSO POSITIVO - Navegador legítimo bloqueado por otra razón - User-Agent: {user_agent}, Referer: {referer}")
                if request_obj:
                    all_headers = dict(request_obj.headers)
                    log.error(f"[_es_bot] Headers completos: {all_headers}")
    
    return resultado

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
    # Obtener User-Agent y Referer para detectar bots/crawlers/link previews
    user_agent = request.headers.get('User-Agent', '')
    referer = request.headers.get('Referer', '')
    is_bot = _es_bot(user_agent, referer, request)
    
    if is_bot:
        # Loggear TODOS los headers para análisis cuando se detecta preview
        all_headers = dict(request.headers)
        log.warning(f"[CAISTE] 🤖 BOT/LINK PREVIEW DETECTADO - User-Agent: {user_agent}, Referer: {referer}, Headers completos: {all_headers} - NO se registrará falla automática")
    
    # Intentar obtener parámetros codificados primero (nueva forma)
    encoded_params = request.args.get('t')
    if encoded_params:
        decoded = decode_phishing_params(encoded_params)
        if decoded:
            idUsuario = decoded.get('idUsuario')
            idEvento = decoded.get('idEvento')
            if idUsuario and idEvento:
                # Solo registrar FALLA si NO es un bot (acceso legítimo del usuario)
                if not is_bot:
                    log.info(f"[CAISTE] Registrando FALLA SIMPLE - Usuario: {idUsuario}, Evento: {idEvento}")
                    ResultadoEventoController.sumarFalla(idUsuario, idEvento)
                else:
                    log.warning(f"[CAISTE] 🤖 BOT DETECTADO - Acceso bloqueado para Usuario: {idUsuario}, Evento: {idEvento} - User-Agent: {user_agent}")
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
        # Solo registrar FALLA si NO es un bot (acceso legítimo del usuario)
        if not is_bot:
            log.info(f"[CAISTE] Registrando FALLA SIMPLE (fallback) - Usuario: {idUsuario}, Evento: {idEvento}")
            ResultadoEventoController.sumarFalla(idUsuario, idEvento)
        else:
            log.warning(f"[CAISTE] 🤖 BOT DETECTADO (fallback) - Acceso bloqueado para Usuario: {idUsuario}, Evento: {idEvento} - User-Agent: {user_agent}")
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
    
    # Obtener User-Agent y Referer para detectar bots/crawlers/link previews
    user_agent = request.headers.get('User-Agent', '')
    referer = request.headers.get('Referer', '')
    is_bot = _es_bot(user_agent, referer, request)
    
    if is_bot:
        # Loggear TODOS los headers para análisis cuando se detecta preview
        all_headers = dict(request.headers)
        log.warning(f"[CAISTE_LOGIN] 🤖 BOT/LINK PREVIEW DETECTADO - User-Agent: {user_agent}, Referer: {referer}, Headers completos: {all_headers} - NO se registrará falla automática")
    else:
        log.info(f"[CAISTE_LOGIN] Acceso legítimo detectado - User-Agent: {user_agent}")
    
    if encoded_params:
        decoded = decode_phishing_params(encoded_params)
        log.info(f"[CAISTE_LOGIN] Parámetros decodificados: {decoded}")
        if decoded:
            idUsuario = decoded.get('idUsuario')
            idEvento = decoded.get('idEvento')
            log.info(f"[CAISTE_LOGIN] idUsuario: {idUsuario}, idEvento: {idEvento}")
            if idUsuario and idEvento:
                # Solo registrar FALLA si NO es un bot (acceso legítimo del usuario)
                if not is_bot:
                    log.info(f"[CAISTE_LOGIN] Registrando FALLA SIMPLE - Usuario: {idUsuario}, Evento: {idEvento}")
                    resultado = ResultadoEventoController.sumarFalla(idUsuario, idEvento)
                    log.info(f"[CAISTE_LOGIN] Resultado de sumarFalla: {resultado}")
                else:
                    log.warning(f"[CAISTE_LOGIN] 🤖 BOT DETECTADO - Acceso bloqueado para Usuario: {idUsuario}, Evento: {idEvento} - User-Agent: {user_agent}")
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
        # Solo registrar FALLA si NO es un bot (acceso legítimo del usuario)
        if not is_bot:
            log.info(f"[CAISTE_LOGIN] Registrando FALLA SIMPLE (fallback) - Usuario: {idUsuario}, Evento: {idEvento}")
            resultado = ResultadoEventoController.sumarFalla(idUsuario, idEvento)
            log.info(f"[CAISTE_LOGIN] Resultado de sumarFalla (fallback): {resultado}")
        else:
            log.warning(f"[CAISTE_LOGIN] 🤖 BOT DETECTADO (fallback) - Acceso bloqueado para Usuario: {idUsuario}, Evento: {idEvento} - User-Agent: {user_agent}")
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
    
    # Obtener User-Agent y Referer para detectar bots/crawlers/link previews
    user_agent = request.headers.get('User-Agent', '')
    referer = request.headers.get('Referer', '')
    is_bot = _es_bot(user_agent, referer, request)
    
    if is_bot:
        # Loggear TODOS los headers para análisis cuando se detecta preview
        all_headers = dict(request.headers)
        log.warning(f"[CAISTE_DATOS] 🤖 BOT/LINK PREVIEW DETECTADO - User-Agent: {user_agent}, Referer: {referer}, Headers completos: {all_headers} - NO se registrará falla automática")
    else:
        log.info(f"[CAISTE_DATOS] Acceso legítimo detectado - User-Agent: {user_agent}")
    
    if encoded_params:
        decoded = decode_phishing_params(encoded_params)
        log.info(f"[CAISTE_DATOS] Parámetros decodificados: {decoded}")
        if decoded:
            idUsuario = decoded.get('idUsuario')
            idEvento = decoded.get('idEvento')
            log.info(f"[CAISTE_DATOS] idUsuario: {idUsuario}, idEvento: {idEvento}")
            if idUsuario and idEvento:
                # Solo registrar FALLA si NO es un bot (acceso legítimo del usuario)
                if not is_bot:
                    log.info(f"[CAISTE_DATOS] Registrando FALLA SIMPLE - Usuario: {idUsuario}, Evento: {idEvento}")
                    resultado = ResultadoEventoController.sumarFalla(idUsuario, idEvento)
                    log.info(f"[CAISTE_DATOS] Resultado de sumarFalla: {resultado}")
                else:
                    log.warning(f"[CAISTE_DATOS] 🤖 BOT DETECTADO - Acceso bloqueado para Usuario: {idUsuario}, Evento: {idEvento} - User-Agent: {user_agent}")
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
        # Solo registrar FALLA si NO es un bot (acceso legítimo del usuario)
        if not is_bot:
            log.info(f"[CAISTE_DATOS] Registrando FALLA SIMPLE (fallback) - Usuario: {idUsuario}, Evento: {idEvento}")
            resultado = ResultadoEventoController.sumarFalla(idUsuario, idEvento)
            log.info(f"[CAISTE_DATOS] Resultado de sumarFalla (fallback): {resultado}")
        else:
            log.warning(f"[CAISTE_DATOS] 🤖 BOT DETECTADO (fallback) - Acceso bloqueado para Usuario: {idUsuario}, Evento: {idEvento} - User-Agent: {user_agent}")
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