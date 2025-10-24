from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    x_bat100 = fields.Boolean(
        string="Batería 100%",
        compute="_compute_x_bat100",
        inverse="_inverse_x_bat100",
        store=False,
    )

    @api.depends('lot_id.x_bat100')
    def _compute_x_bat100(self):
        for line in self:
            line.x_bat100 = line.lot_id.x_bat100 if line.lot_id else False

    def _inverse_x_bat100(self):
        for line in self:
            if line.lot_id:
                line.lot_id.x_bat100 = line.x_bat100
