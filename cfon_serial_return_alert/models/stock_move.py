
# -*- coding: utf-8 -*-
from odoo import models

class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        lines = self.mapped('move_line_ids').filtered(
            lambda l: l.state == 'done' and l.location_id.usage == 'customer' and l.location_dest_id.usage == 'internal' and l.lot_id
        )
        lots = lines.mapped('lot_id')
        lots.action_notify_if_needed()
        return res
