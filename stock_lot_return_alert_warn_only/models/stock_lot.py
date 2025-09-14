
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockLot(models.Model):
    _inherit = "stock.lot"

    return_count = fields.Integer(
        string="Customer Returns Count",
        compute="_compute_return_count",
        store=True,
        help="Number of times this serial/lot came back from a Customer to an Internal location (done moves).",
    )
    returned_many_times = fields.Boolean(
        string="Returned Many Times",
        compute="_compute_return_count",
        store=True,
        help="True if return_count >= company threshold.",
    )

    @api.depends('quant_ids.quantity')  # dummy dep to allow recompute from cron via invalidate
    def _compute_return_count(self):
        MoveLine = self.env['stock.move.line']
        for lot in self:
            # Count DONE moves from a customer location to an internal location involving this lot/serial
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
        """Create an activity on the lot when threshold is reached/exceeded."""
        Activity = self.env['mail.activity']
        activity_type = self.env.ref('mail.mail_activity_data_todo')
        for lot in self:
            threshold = lot.company_id.return_alert_threshold or 2
            if lot.return_count >= threshold:
                # Avoid duplicate activity if an open one exists about this topic
                existing = Activity.search([
                    ('res_id', '=', lot.id),
                    ('res_model', '=', lot._name),
                    ('summary', '=', "Serial/lot returned many times"),
                    ('active', '=', True),
                ], limit=1)
                if existing:
                    continue
                user_id = lot.company_id.return_alert_responsible_id.id or False
                vals = {
                    'res_id': lot.id,
                    'res_model_id': self.env['ir.model']._get_id(lot._name),
                    'activity_type_id': activity_type.id,
                    'summary': "Serial/lot returned many times",
                    'note': _("The serial/lot %s (Product: %s) has been returned from Customer to Stock %s times. Please investigate.")
                            % (lot.name or '-', lot.product_id.display_name or '-', lot.return_count),
                }
                if user_id:
                    vals['user_id'] = user_id
                Activity.create(vals)

    def action_view_return_moves(self):
        """Smart button to view return moves for this lot."""
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id("stock.stock_move_line_action")
        action['domain'] = [
            ('lot_id', '=', self.id),
            ('state', '=', 'done'),
            ('location_id.usage', '=', 'customer'),
            ('location_dest_id.usage', '=', 'internal'),
        ]
        action['name'] = _("Customer Returns for %s") % (self.name or '')
        return action
