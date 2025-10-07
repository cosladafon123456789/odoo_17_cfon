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

        url = "https://imeicheck.net/check_icloud.php"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Odoo17; +https://cosladafon.com)",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://imeicheck.net/"
        }
        data = {"imei": imei}

        try:
            response = requests.post(url, data=data, headers=headers, timeout=25)
            if response.status_code >= 400:
                raise UserError(_("No se pudo contactar con el servicio de verificación (HTTP %s).") % response.status_code)

            html = response.text or ""
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(" ", strip=True).upper()

            # Buscar la línea "FIND MY DEVICE: ON/OFF"
            status = None
            m = re.search(r"FIND\s+MY\s+DEVICE\s*[:\-]?\s*(ON|OFF)", text, flags=re.I)
            if m:
                status = m.group(1).upper()

            if not status:
                # Buscar visualmente el texto dentro del HTML
                label = soup.find(string=lambda t: t and "Find My Device" in t)
                if label:
                    el = getattr(label, "parent", None)
                    if el:
                        nxt = el.find_next(["strong", "span", "b", "td", "div"])
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
