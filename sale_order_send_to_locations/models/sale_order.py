from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_open_send_to_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enviar a ubicación',
            'res_model': 'send.to.location.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_id': self.id
            }
        }
