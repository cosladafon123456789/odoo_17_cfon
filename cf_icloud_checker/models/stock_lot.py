from odoo import models, _
from odoo.exceptions import UserError
import requests
from bs4 import BeautifulSoup
import re

class StockLot(models.Model):
    _inherit = "stock.lot"

    def action_check_icloud(self):
        self.ensure_one()
        imei = (self.name or "").strip()
        if not imei:
            raise UserError(_("No se encontró número de serie / IMEI en este registro."))

        url = "https://iunlocker.net/check_icloud.php"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Odoo17; +https://cosladafon.com)",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Referer": "https://iunlocker.net/"
        }
        data = {"imei": imei}

        try:
            # Petición directa, sin JS
            response = requests.post(url, data=data, headers=headers, timeout=25)
            if response.status_code >= 400:
                raise UserError(_("No se pudo contactar con el servicio de verificación (HTTP %s).") % response.status_code)

            html = response.text or ""
            soup = BeautifulSoup(html, "html.parser")

            # 1) Búsqueda por regex robusta en todo el texto
            text = soup.get_text(" ", strip=True)
            m = re.search(r"iCloud\\s*Lock\\s*[:\\-]?\\s*(ON|OFF)", text, flags=re.I)
            status = None
            if m:
                status = m.group(1).upper()

            # 2) Si no, intentar localizar por etiquetas cercanas
            if not status:
                label = soup.find(string=lambda t: t and "iCloud" in t and "Lock" in t)
                if label:
                    el = getattr(label, "parent", None)
                    if el:
                        nxt = el.find_next(["strong", "b", "span", "td", "div"])
                        if nxt:
                            val = nxt.get_text(strip=True).upper()
                            if "OFF" in val:
                                status = "OFF"
                            elif "ON" in val:
                                status = "ON"

            if not status:
                # Mensaje neutro si no se pudo extraer
                raise UserError(_("No se pudo determinar el estado de iCloud para el IMEI indicado."))

            if status == "OFF":
                message = "iCloud: OFF"
            elif status == "ON":
                message = "iCloud: ON"
            else:
                message = "iCloud: %s" % status

            return {
                "effect": {
                    "fadeout": "slow",
                    "message": message,
                    "type": "rainbow_man",
                }
            }

        except Exception as e:
            raise UserError(_("Error al comprobar iCloud: %s") % str(e))
