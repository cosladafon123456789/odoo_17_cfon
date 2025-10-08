from odoo import models, fields
import re

class SaleBlacklist(models.Model):
    _name = "sale.blacklist"
    _description = "Sale Blacklist / Fraud blocking"

    name = fields.Char(string="Etiqueta", required=True)
    active = fields.Boolean(default=True)
    zip = fields.Char(string="Código Postal")
    city = fields.Char(string="Ciudad")
    phone = fields.Char(string="Teléfono")
    email = fields.Char(string="Email")
    address_substring = fields.Char(string="Texto dirección (substring)")
    name_regex = fields.Char(string="Regex nombre (expresion regular)")
    note = fields.Text(string="Observaciones")

    def matches_partner(self, partner):
        if not self.active:
            return False

        if self.phone and partner.phone:
            if self.phone.replace(" ", "") == (partner.phone or "").replace(" ", ""):
                return True

        if self.email and partner.email:
            if self.email.lower() == (partner.email or "").lower():
                return True

        if self.zip and self.city:
            if (partner.zip and partner.zip.strip() == self.zip.strip()) and                (partner.city and partner.city.lower().strip() == self.city.lower().strip()):
                return True

        if self.address_substring:
            addr = (partner.street or "") + " " + (partner.street2 or "")
            if self.address_substring.lower().strip() in addr.lower():
                return True

        if self.name_regex and partner.name:
            try:
                if re.search(self.name_regex, partner.name, flags=re.IGNORECASE):
                    return True
            except re.error:
                pass
        return False
