from odoo import models, fields
from odoo.exceptions import ValidationError
import re

class SaleBlacklist(models.Model):
    _name = 'sale.blacklist'
    _description = 'Lista negra de clientes (envíos bloqueados)'

    name = fields.Char(string='Etiqueta', required=True)
    active = fields.Boolean(default=True)
    zip = fields.Char(string='Código Postal')
    city = fields.Char(string='Ciudad')
    phone = fields.Char(string='Teléfono')
    email = fields.Char(string='Email')
    address_substring = fields.Char(string='Texto dirección (substring)')
    name_regex = fields.Char(string='Regex nombre (expresión regular)')
    note = fields.Text(string='Motivo / Observaciones')

    def _match_partner(self, partner):
        if not self.active:
            return False
        # CP y ciudad
        if self.zip and not self.city:
            if partner.zip and partner.zip.strip() == self.zip.strip():
                return True
        elif self.zip and self.city:
            if (partner.zip and partner.zip.strip() == self.zip.strip()) and                (partner.city and partner.city.lower().strip() == self.city.lower().strip()):
                return True
        # Teléfono
        if self.phone and partner.phone and partner.phone.strip() == self.phone.strip():
            return True
        # Email
        if self.email and partner.email and partner.email.strip() == self.email.strip():
            return True
        # Dirección contiene texto
        if self.address_substring and partner.street and self.address_substring.lower() in partner.street.lower():
            return True
        # Regex nombre
        if self.name_regex and re.search(self.name_regex, partner.name or '', re.IGNORECASE):
            return True
        return False

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for picking in self:
            partner = picking.partner_id
            if not partner:
                continue
            blacklist_records = self.env['sale.blacklist'].search([('active', '=', True)])
            for bl in blacklist_records:
                if bl._match_partner(partner):
                    raise ValidationError(
                        f"Pedido bloqueado: el cliente coincide con la lista negra ({bl.name}).\nMotivo: {bl.note or 'Sin motivo especificado.'}"
                    )
        return super().button_validate()
