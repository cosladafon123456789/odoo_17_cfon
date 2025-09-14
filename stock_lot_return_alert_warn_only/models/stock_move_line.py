
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.onchange('lot_id')
    def _onchange_lot_warn_many_returns(self):
        for line in self:
            if line.lot_id and line.lot_id.returned_many_times:
                threshold = line.company_id.return_alert_threshold or line.company_id.sudo().return_alert_threshold or 2
                return {
                    'warning': {
                        'title': _("Serial returned many times"),
                        'message': _("The serial/lot %(lot)s (Product: %(prod)s) has been returned %(n)d times (≥ threshold %(th)d). Please review before delivering.") % {
                            'lot': line.lot_id.name or '-',
                            'prod': line.product_id.display_name or '-',
                            'n': line.lot_id.return_count,
                            'th': threshold,
                        }
                    }
                }
        return {}

