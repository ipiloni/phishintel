"""
Módulo para manejar el túnel de Cloudflare de forma automática.
Inicia el túnel cuando DESPLIEGUE_LOCAL = SI en properties.env
"""
import os
import subprocess
import threading
import time
from pathlib import Path
from app.utils.config import get
from app.utils.logger import log


class CloudflareTunnel:
    """Clase para manejar el túnel de Cloudflare"""
    
    def __init__(self):
        self.process = None
        self.tunnel_thread = None
        self.cloudflared_dir = Path(__file__).resolve().parent.parent / 'cloudflared'
        self.config_file = self.cloudflared_dir / 'config.yml'
        
    def is_enabled(self):
        """Verifica si el despliegue local está habilitado"""
        despliegue_local = get('DESPLIEGUE_LOCAL')
        return despliegue_local and despliegue_local.strip().upper() == 'SI'
    
    def check_cloudflared_installed(self):
        """Verifica si cloudflared está instalado en el sistema"""
        try:
            result = subprocess.run(
                ['cloudflared', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def check_config_exists(self):
        """Verifica si el archivo de configuración existe"""
        return self.config_file.exists()
    
    def start_tunnel(self):
        """Inicia el túnel de Cloudflare en un proceso separado"""
        if not self.is_enabled():
            return False
        
        log.info("Verificando configuración para túnel Cloudflare...")
        
        # Verificar si cloudflared está instalado
        if not self.check_cloudflared_installed():
            log.error("cloudflared no está instalado o no está en el PATH")
            log.info("   Instala cloudflared desde: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/")
            return False
        
        # Verificar si existe el archivo de configuración
        if not self.check_config_exists():
            log.error(f"No se encontró el archivo de configuración: {self.config_file}")
            log.info("   Asegúrate de que config.yml existe en la carpeta cloudflared/")
            return False
        
        try:
            # Leer el nombre del túnel del config.yml
            tunnel_name = self._get_tunnel_name()
            log.info(f"Iniciando túnel Cloudflare '{tunnel_name}'...")
            
            # Iniciar el proceso de cloudflared
            self.process = subprocess.Popen(
                ['cloudflared', 'tunnel', 'run', tunnel_name],
                cwd=str(self.cloudflared_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Esperar un momento para verificar si el proceso se inició correctamente
            time.sleep(2)
            
            if self.process.poll() is not None:
                # El proceso terminó inmediatamente, algo salió mal
                stdout, stderr = self.process.communicate()
                log.error("Error al iniciar el túnel Cloudflare")
                if stderr:
                    log.error(f"   Error: {stderr.strip()}")
                if stdout:
                    log.error(f"   Output: {stdout.strip()}")
                return False
            
            log.success(f"Túnel Cloudflare iniciado correctamente (PID: {self.process.pid})")
            
            # Iniciar un hilo para monitorear el proceso
            self.tunnel_thread = threading.Thread(
                target=self._monitor_tunnel,
                daemon=True
            )
            self.tunnel_thread.start()
            
            return True
            
        except Exception as e:
            log.error(f"Error al iniciar el túnel Cloudflare: {str(e)}")
            return False
    
    def _get_tunnel_name(self):
        """Obtiene el nombre del túnel del archivo config.yml"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('tunnel:'):
                        tunnel_name = line.split(':', 1)[1].strip()
                        return tunnel_name
            # Si no se encuentra, usar el nombre por defecto
            return 'phishintel-tunnel'
        except Exception as e:
            log.warning(f"No se pudo leer el nombre del túnel del config.yml: {e}. Usando 'phishintel-tunnel' por defecto.")
            return 'phishintel-tunnel'
    
    def _monitor_tunnel(self):
        """Monitorea el proceso del túnel en segundo plano"""
        try:
            stdout, stderr = self.process.communicate()
            if self.process.returncode != 0:
                log.error(f"El túnel Cloudflare se detuvo inesperadamente (código: {self.process.returncode})")
                if stderr:
                    log.error(f"Error: {stderr}")
            else:
                log.info("Túnel Cloudflare detenido correctamente")
        except Exception as e:
            log.error(f"Error al monitorear el túnel: {str(e)}")
    
    def stop_tunnel(self):
        """Detiene el túnel de Cloudflare"""
        if self.process and self.process.poll() is None:
            log.info("Deteniendo túnel Cloudflare...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                log.info("Túnel Cloudflare detenido correctamente")
            except subprocess.TimeoutExpired:
                log.warning("El túnel no se detuvo a tiempo, forzando cierre...")
                self.process.kill()
                self.process.wait()
                log.info("Túnel Cloudflare forzado a cerrar")
            self.process = None


# Instancia global del túnel
tunnel_manager = CloudflareTunnel()

