from odoo import models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _check_blacklist_partner(self, partner):
        blacklists = self.env['sale.blacklist'].search([('active','=',True)])
        for bl in blacklists:
            if bl.matches_partner(partner):
                return bl
        return False

    def action_confirm(self):
        for order in self:
            partner = order.partner_id
            bl = self._check_blacklist_partner(partner)
            if bl:
                raise UserError(
                    f"Pedido bloqueado: el cliente coincide con la lista negra ({bl.name}).\nMotivo: {bl.note or 'sin motivo'}"
                )
        return super().action_confirm()
