
# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    x_bat100 = fields.Boolean(string='Batería 100%')

    @api.onchange('x_bat100')
    def _onchange_x_bat100(self):
        """Sincroniza con el lote cuando se marque desde la línea."""
        for line in self:
            if line.lot_id:
                line.lot_id.x_bat100 = line.x_bat100
