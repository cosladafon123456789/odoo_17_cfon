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
            response = requests.post(url, data=data, headers=headers, timeout=20)
            soup = BeautifulSoup(response.text, "html.parser")

            # Buscar el texto del estado iCloud dentro de la página
            icloud_label = soup.find(text=lambda t: "iCloud Lock" in t)
            if not icloud_label:
                raise UserError(_("No se pudo leer el estado de iCloud en la respuesta."))

            # Buscar el valor (OFF/ON) cercano a esa etiqueta
            value_tag = None
            if icloud_label.parent:
                value_tag = icloud_label.parent.find_next("td")
            if not value_tag:
                value_tag = soup.find(string=lambda t: t and "OFF" in t or "ON" in t)

            text = (value_tag.get_text() if hasattr(value_tag, "get_text") else str(value_tag)).upper()

            if "OFF" in text:
                message = "iCloud: OFF"
            elif "ON" in text:
                message = "iCloud: ON"
            else:
                message = "iCloud: No se pudo determinar"

            return {
                "effect": {
                    "fadeout": "slow",
                    "message": message,
                    "type": "rainbow_man"
                },
            }

        except Exception as e:
            raise UserError(_("Error al comprobar iCloud: %s") % str(e))
