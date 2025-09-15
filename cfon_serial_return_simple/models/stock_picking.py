
# -*- coding: utf-8 -*-
from odoo import models, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            for ml in picking.move_line_ids:
                lot = ml.lot_id
                if not lot:
                    continue
                move = ml.move_id
                try:
                    if move.location_id.usage == 'customer' and move.location_dest_id.usage == 'internal':
                        if (ml.qty_done or 0.0) > 0:
                            lot.return_count += 1
                            if lot.return_count == 2:
                                lot.message_post(
                                    body=_("This serial/lot has been returned to stock at least 2 times (latest picking: %s).") % (picking.name or picking.id),
                                    subtype_xmlid="mail.mt_note",
                                )
                except Exception:
                    pass
        return res
