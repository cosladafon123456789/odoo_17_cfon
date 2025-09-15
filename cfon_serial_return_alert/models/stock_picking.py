
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    has_many_return_serials = fields.Boolean(
        string="Has serials with 2+ returns",
        compute="_compute_has_many_return_serials",
        store=False,
    )
    many_return_lot_count = fields.Integer(
        string="Serials 2+ returns (count)",
        compute="_compute_has_many_return_serials",
        store=False,
    )

    @api.depends('move_line_ids.lot_id', 'move_line_ids.lot_id.return_count')
    def _compute_has_many_return_serials(self):
        for picking in self:
            lots = picking.move_line_ids.filtered(lambda ml: ml.lot_id).mapped('lot_id')
            flagged = [l for l in lots if l.return_count >= 2]
            picking.has_many_return_serials = bool(flagged)
            picking.many_return_lot_count = len(set(flagged))

    def button_validate(self):
        """On validation, if it contains moves that return from Customer to Internal,
        increment the return_count on the involved lots.
        """
        res = super().button_validate()
        # Only increment for moves that flow from customer->internal
        for picking in self:
            for ml in picking.move_line_ids:
                lot = ml.lot_id
                if not lot:
                    continue
                move = ml.move_id
                try:
                    if move.location_id.usage == 'customer' and move.location_dest_id.usage == 'internal':
                        qty = ml.qty_done or 0.0
                        if qty > 0:
                            # increment once per move line occurrence (not by qty)
                            lot.return_count += 1
                            # If threshold reached for the first time, post a message for traceability
                            if lot.return_count == 2:
                                lot.message_post(
                                    body=_("This serial/lot has been returned to stock at least 2 times (latest picking: %s).") % (picking.name or picking.id),
                                    subtype_xmlid="mail.mt_note",
                                )
                except Exception:
                    # Be defensive: never block validation
                    pass
        return res

    def action_open_many_return_lots(self):
        self.ensure_one()
        lots = self.move_line_ids.filtered(lambda ml: ml.lot_id and ml.lot_id.return_count >= 2).mapped('lot_id').ids
        action = self.env.ref('stock.action_production_lot_form').read()[0]
        action['domain'] = [('id', 'in', lots)]
        action['name'] = _("Serials returned 2+ times in %s") % (self.name or 'Picking')
        return action
