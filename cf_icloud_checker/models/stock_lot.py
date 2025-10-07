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

        url = "https://iunlocker.com/check_icloud.php"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Odoo17; +https://cosladafon.com)",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Referer": "https://iunlocker.com/"
        }
        data = {"imei": imei}

        try:
            response = requests.post(url, data=data, headers=headers, timeout=25)
            if response.status_code >= 400:
                raise UserError(_("No se pudo contactar con el servicio de verificación (HTTP %s).") % response.status_code)

            html = response.text or ""
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(" ", strip=True).upper()

            # Buscar OFF o ON en el texto de la página
            status = None
            if re.search(r"ICLOUD\s*LOCK\s*[:\-]?\s*OFF", text):
                status = "OFF"
            elif re.search(r"ICLOUD\s*LOCK\s*[:\-]?\s*ON", text):
                status = "ON"

            if not status:
                # Intentar localizar manualmente
                label = soup.find(string=lambda t: t and "iCloud Lock" in t)
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
