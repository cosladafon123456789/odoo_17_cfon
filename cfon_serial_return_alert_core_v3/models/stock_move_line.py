# -*- coding: utf-8 -*-
from odoo import api, models, _

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.onchange('lot_id')
    def _onchange_lot_warn_many_returns(self):
        for line in self:
            if line.lot_id and line.product_id and line.product_id.tracking != 'none':
                lot = line.lot_id
                lot._compute_return_count()
                if lot.returned_many_times:
                    threshold = lot._get_threshold()
                    return {
                        'warning': {
                            'title': _("Serial returned many times"),
                            'message': _("The serial/lot %(lot)s (Product: %(prod)s) has been returned %(n)d times (≥ threshold %(th)d). Please review before delivering.") % {
                                'lot': lot.name or '-',
                                'prod': line.product_id.display_name or '-',
                                'n': lot.return_count,
                                'th': threshold,
                            }
                        }
                    }
        return {}
