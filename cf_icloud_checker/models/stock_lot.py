from odoo import models, _
from odoo.exceptions import UserError
import requests
from bs4 import BeautifulSoup
import re

IMEICHECK_HOME = "https://imeicheck.net/"
IMEICHECK_POST = "https://imeicheck.net/check_icloud.php"

class StockLot(models.Model):
    _inherit = "stock.lot"

    def action_check_icloud(self):
        self.ensure_one()
        imei = (self.name or "").strip()
        if not imei:
            raise UserError(_("No se encontró número de serie / IMEI en este registro."))

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,es-ES;q=0.8,es;q=0.7",
            "Referer": IMEICHECK_HOME,
        }

        try:
            s = requests.Session()
            s.headers.update(headers)

            # 1) Abrir la home para obtener cookies válidas
            s.get(IMEICHECK_HOME, timeout=20)

            # 2) Enviar el IMEI al endpoint conocido (la web redirige a la página de resultado)
            resp = s.post(IMEICHECK_POST, data={"imei": imei}, timeout=25, allow_redirects=True)

            if resp.status_code >= 400:
                raise UserError(_("No se pudo contactar con el servicio (HTTP %s).") % resp.status_code)

            html = resp.text or ""
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(" ", strip=True)

            # 3) Buscar el resultado "Find My Device: ON/OFF"
            status = None
            m = re.search(r"Find\s+My\s+Device\s*[:\-]?\s*(ON|OFF)", text, flags=re.I)
            if m:
                status = m.group(1).upper()
            else:
                # Intento adicional: localizar por etiquetas vecinas
                label = soup.find(string=lambda t: t and "Find My Device" in t)
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

            message = f"iCloud: {status}"

            return {
                "effect": {
                    "fadeout": "slow",
                    "message": message,
                    "type": "rainbow_man",
                }
            }

        except Exception as e:
            raise UserError(_("Error al comprobar iCloud: %s") % str(e))
