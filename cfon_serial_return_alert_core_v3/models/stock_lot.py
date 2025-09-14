# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockLot(models.Model):
    _inherit = "stock.lot"

    return_count = fields.Integer(
        string="Customer Returns Count",
        compute="_compute_return_count",
        help="Number of times this serial/lot came back from a Customer to an Internal location (done moves).",
    )
    returned_many_times = fields.Boolean(
        string="Returned Many Times",
        compute="_compute_return_count",
        help="True if return_count >= threshold.",
    )

    def _get_threshold(self):
        icp = self.env['ir.config_parameter'].sudo()
        v = icp.get_param('cfon_serial_return.threshold')
        try:
            th = int(v)
            if th < 1:
                th = 1
        except Exception:
            th = 2
        return th

    def _get_responsible_user(self):
        icp = self.env['ir.config_parameter'].sudo()
        v = icp.get_param('cfon_serial_return.user_id')
        try:
            uid = int(v)
        except Exception:
            uid = False
        return self.env['res.users'].browse(uid) if uid else False

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
            threshold = self._get_threshold()
            lot.returned_many_times = count >= threshold

    def action_notify_if_needed(self):
        Activity = self.env['mail.activity']
        activity_type = self.env.ref('mail.mail_activity_data_todo')
        for lot in self:
            lot._compute_return_count()
            threshold = self._get_threshold()
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
                user = self._get_responsible_user()
                if user and user.exists():
                    vals['user_id'] = user.id
                Activity.create(vals)
