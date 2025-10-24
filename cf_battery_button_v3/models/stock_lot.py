from odoo import models, fields, api

class StockLot(models.Model):
    _inherit = 'stock.lot'

    x_bat100 = fields.Boolean(string="Batería 100%", default=False)

    @api.model
    def action_toggle_bat100(self):
        """Alterna el estado de Batería 100%"""
        for record in self:
            record.x_bat100 = not record.x_bat100
        return True
