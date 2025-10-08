from odoo import models
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        for pick in self:
            partner = pick.partner_id or (pick.sale_id.partner_id if pick.sale_id else False)
            if partner:
                bl = self.env['sale.blacklist'].search([('active','=',True)])
                for b in bl:
                    if b.matches_partner(partner):
                        raise UserError(f"Entrega bloqueada: el destinatario coincide con la lista negra ({b.name}).")
        return super().button_validate()
