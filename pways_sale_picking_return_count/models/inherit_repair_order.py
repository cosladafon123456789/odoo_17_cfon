from odoo import fields, models, api

class RepairOrder(models.Model):
    _inherit = 'repair.order'

    has_more_return_count = fields.Boolean(
        string="Has More Return Count",
        compute="_compute_has_more_return_batches",
        store=False
    )

    def _compute_has_more_return_batches(self):
        for move in self:
            if move.lot_id and move.lot_id.return_count >= 2:
                move.has_more_return_count=True
            else:
                move.has_more_return_count=False