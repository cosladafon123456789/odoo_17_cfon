from odoo import models, _
from odoo.exceptions import UserError
import requests
from bs4 import BeautifulSoup

class StockLot(models.Model):
    _inherit = "stock.lot"

    def action_check_icloud(self):
        self.ensure_one()
        imei = (self.name or "").strip()
        if not imei:
            raise UserError(_("No se encontró número de serie / IMEI en este registro."))

        url = "https://iunlocker.com/es/check_icloud.php"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Odoo17; +https://cosladafon.com)",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        }
        data = {"imei": imei}

        try:
            response = requests.post(url, data=data, headers=headers, timeout=25)
            soup = BeautifulSoup(response.text, "html.parser")

            # Buscar el bloque donde se muestra el estado "iCloud Lock"
            result_label = soup.find(string=lambda t: t and "iCloud Lock" in t)
            if not result_label:
                raise UserError(_("No se pudo leer el estado de iCloud en la respuesta."))

            # Buscar la palabra ON u OFF cerca de ese texto
            parent = result_label.find_parent()
            value_text = None

            if parent:
                # Buscar dentro de los elementos cercanos
                value_el = parent.find_next(["strong", "span", "td"])
                if value_el:
                    value_text = value_el.get_text(strip=True).upper()

            # Fallback si no lo encuentra directamente
            if not value_text:
                text = soup.get_text(" ", strip=True).upper()
                if "ICLOUD LOCK OFF" in text:
                    value_text = "OFF"
                elif "ICLOUD LOCK ON" in text:
                    value_text = "ON"

            if not value_text:
                raise UserError(_("No se pudo leer el estado de iCloud en la respuesta."))

            # Determinar el resultado final
            if "OFF" in value_text:
                message = "✅ iCloud: OFF (libre)"
            elif "ON" in value_text:
                message = "🔒 iCloud: ON (bloqueado)"
            else:
                message = f"iCloud: {value_text}"

            return {
                "effect": {
                    "fadeout": "slow",
                    "message": message,
                    "type": "rainbow_man",
                }
            }

        except Exception as e:
            raise UserError(_("Error al comprobar iCloud: %s") % str(e))
