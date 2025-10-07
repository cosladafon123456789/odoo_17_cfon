import subprocess
import sys
import logging

_logger = logging.getLogger(__name__)

def _install_cloudscraper():
    try:
        import cloudscraper
        _logger.info("✅ El paquete 'cloudscraper' ya está instalado.")
    except ImportError:
        _logger.warning("⚠️ El paquete 'cloudscraper' no está instalado. Intentando instalarlo...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "cloudscraper"])
            _logger.info("✅ 'cloudscraper' instalado correctamente.")
        except Exception as e:
            _logger.error(f"❌ Error al instalar cloudscraper: {e}")

def post_init_hook(env):
    """Se ejecuta automáticamente tras instalar el módulo."""
    _install_cloudscraper()
