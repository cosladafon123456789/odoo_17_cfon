from odoo import fields, models

class StockLot(models.Model):
    _inherit = 'stock.lot'

    x_bat100 = fields.Boolean(string='Batería 100%')

    def action_toggle_bat100(self):
        for lot in self:
            lot.x_bat100 = not lot.x_bat100


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    x_bat100 = fields.Boolean(
        string="Batería 100%",
        related="lot_id.x_bat100",
        store=False,
    )
