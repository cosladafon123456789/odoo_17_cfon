from odoo import models, fields

class StockLot(models.Model):
    _inherit = 'stock.lot'

    x_bat100 = fields.Boolean(string="Batería 100%", default=False)

    def action_toggle_bat100(self):
        for record in self:
            record.x_bat100 = not record.x_bat100
