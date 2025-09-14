
# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        # After validation, check for any move lines that are customer -> internal (returns)
        lines = self.mapped('move_line_ids').filtered(
            lambda l: l.state == 'done' and l.location_id.usage == 'customer' and l.location_dest_id.usage == 'internal' and l.lot_id
        )
        lots = lines.mapped('lot_id')
        # Recompute and notify
        lots.invalidate_model(['return_count', 'returned_many_times'])
        for lot in lots:
            lot._compute_return_count()
        lots.action_notify_if_needed()
        return res
