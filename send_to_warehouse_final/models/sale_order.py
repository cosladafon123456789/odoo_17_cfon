from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_open_send_to_warehouse_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enviar a Almacén',
            'res_model': 'send.to.warehouse.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
            }
        }