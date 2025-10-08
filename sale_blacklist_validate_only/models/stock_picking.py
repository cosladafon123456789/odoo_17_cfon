from odoo import models
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        for pick in self:
            partner = pick.partner_id or (pick.sale_id.partner_id if pick.sale_id else False)
            if partner:
                blacklists = self.env['sale.blacklist'].search([('active', '=', True)])
                for bl in blacklists:
                    if bl.matches_partner(partner):
                        raise UserError(
                            f"⚠️ Entrega bloqueada: el destinatario coincide con la lista negra ({bl.name}).\n"
                            f"Motivo: {bl.note or 'Sin motivo especificado.'}"
                        )
        return super().button_validate()
