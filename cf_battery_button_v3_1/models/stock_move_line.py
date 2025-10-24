from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    x_bat100 = fields.Boolean(string="Batería 100%", default=False)

    @api.onchange('lot_id')
    def _onchange_lot_id_sync_bat100(self):
        if self.lot_id:
            self.x_bat100 = self.lot_id.x_bat100

    @api.onchange('x_bat100')
    def _onchange_x_bat100(self):
        if self.lot_id:
            self.lot_id.x_bat100 = self.x_bat100
