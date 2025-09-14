
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockLot(models.Model):
    _inherit = "stock.lot"

    # Non-stored -> computed on demand to avoid install boot issues
    return_count = fields.Integer(
        string="Customer Returns Count",
        compute="_compute_return_count",
        help="Number of times this serial/lot came back from a Customer to an Internal location (done moves).",
    )
    returned_many_times = fields.Boolean(
        string="Returned Many Times",
        compute="_compute_return_count",
        help="True if return_count >= company threshold.",
    )

    def _compute_return_count(self):
        MoveLine = self.env['stock.move.line']
        for lot in self:
            domain = [
                ('lot_id', '=', lot.id),
                ('state', '=', 'done'),
                ('location_id.usage', '=', 'customer'),
                ('location_dest_id.usage', '=', 'internal'),
            ]
            count = MoveLine.search_count(domain)
            lot.return_count = count
            threshold = lot.company_id.return_alert_threshold or 2
            lot.returned_many_times = count >= threshold

    def action_notify_if_needed(self):
        """Create a To-Do activity on the lot when threshold is reached/exceeded."""
        Activity = self.env['mail.activity']
        activity_type = self.env.ref('mail.mail_activity_data_todo')
        for lot in self:
            lot._compute_return_count()
            threshold = lot.company_id.return_alert_threshold or 2
            if lot.return_count >= threshold:
                existing = Activity.search([
                    ('res_id', '=', lot.id),
                    ('res_model', '=', lot._name),
                    ('summary', '=', "Serial/lot returned many times"),
                    ('active', '=', True),
                ], limit=1)
                if existing:
                    continue
                vals = {
                    'res_id': lot.id,
                    'res_model_id': self.env['ir.model']._get_id(lot._name),
                    'activity_type_id': activity_type.id,
                    'summary': "Serial/lot returned many times",
                    'note': _("The serial/lot %s (Product: %s) has been returned from Customer to Stock %s times. Please investigate.")
                            % (lot.name or '-', lot.product_id.display_name or '-', lot.return_count),
                }
                user = lot.company_id.return_alert_responsible_id
                if user:
                    vals['user_id'] = user.id
                Activity.create(vals)

    def action_view_return_moves(self):
        """Open return move lines for this lot (no fragile xmlid)."""
        self.ensure_one()
        return {
            'name': _("Customer Returns for %s") % (self.name or ''),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move.line',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [
                ('lot_id', '=', self.id),
                ('state', '=', 'done'),
                ('location_id.usage', '=', 'customer'),
                ('location_dest_id.usage', '=', 'internal'),
            ],
            'context': {'search_default_groupby_picking': 1},
        }
