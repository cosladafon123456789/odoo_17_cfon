from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def open_enviar_a_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enviar A',
            'res_model': 'enviar.a.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }
