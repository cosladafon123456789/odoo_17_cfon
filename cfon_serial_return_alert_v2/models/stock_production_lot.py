
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    return_count = fields.Integer(
        string="Return count",
        help="Times this serial/lot has been returned from a Customer to Internal stock.",
        default=0,
        readonly=True,
    )

    def action_open_moves_history(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_line_action').read()[0]
        action['domain'] = [('lot_id', '=', self.id)]
        action['name'] = _("Moves for %s") % (self.name or 'Lot')
        return action
