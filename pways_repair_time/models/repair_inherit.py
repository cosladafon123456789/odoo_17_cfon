from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class RepairOrder(models.Model):
    _inherit = "repair.order"

    order_minutes = fields.Float(string='Order Minutes', compute='_compute_order_minutes', search='_search_order_minutes', copy=False)
    done_date = fields.Datetime(string='Done Date', copy=False, readonly=True)


    def write(self, vals):
        if 'state' in vals:
            for rec in self:
                if vals['state'] == 'done' and not rec.done_date:
                    vals['done_date'] = fields.Datetime.now()
        return super().write(vals)


    @api.depends('done_date')
    def _compute_order_minutes(self):
        now = fields.Datetime.now()
        for rec in self:
            if rec.done_date:
                delta = now - rec.done_date
                rec.order_minutes = delta.total_seconds() / 60.0
            else:
                rec.order_minutes = 0.0


    def _search_order_minutes(self, operator, value):
        now = fields.Datetime.now()
        threshold = now - timedelta(minutes=value)

        reverse_operator = {
            '<=': '>=',
            '<':  '>',
            '>=': '<=',
            '>':  '<',
            '=':  '=',
            '!=': '!='
        }.get(operator)

        if not reverse_operator:
            raise ValueError(f"Unsupported operator: {operator}")

        return [('done_date', reverse_operator, threshold)]