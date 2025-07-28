
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_open_send_to_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send To Location',
            'res_model': 'send.to.location.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }
