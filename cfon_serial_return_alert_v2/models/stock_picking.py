
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    many_return_lot_count = fields.Integer(
        string="Serials 2+ returns (count)",
        compute="_compute_many_return_lot_count",
        store=False,
    )

    @api.depends('move_line_ids.lot_id', 'move_line_ids.lot_id.return_count')
    def _compute_many_return_lot_count(self):
        for picking in self:
            lots = picking.move_line_ids.filtered(lambda ml: ml.lot_id).mapped('lot_id')
            flagged = [l for l in lots if l.return_count >= 2]
            picking.many_return_lot_count = len(set(flagged))

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
                            # increment once per move line
                            lot.return_count += 1
                            if lot.return_count == 2:
                                lot.message_post(
                                    body=_("This serial/lot has been returned to stock at least 2 times (latest picking: %s).") % (picking.name or picking.id),
                                    subtype_xmlid="mail.mt_note",
                                )
                except Exception:
                    pass
        return res

    def action_open_many_return_lots(self):
        self.ensure_one()
        lots = self.move_line_ids.filtered(lambda ml: ml.lot_id and ml.lot_id.return_count >= 2).mapped('lot_id').ids
        action = self.env.ref('stock.action_production_lot_form').read()[0]
        action['domain'] = [('id', 'in', lots)]
        action['name'] = _("Serials returned 2+ times in %s") % (self.name or 'Picking')
        return action
