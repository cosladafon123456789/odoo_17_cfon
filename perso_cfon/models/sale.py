# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    #GAP V1
    is_rebu = fields.Boolean(string=_("Is REBU"), default=False)

    #GAP V1
    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for r in res:
            if r.is_rebu:
                r.order_line.write({'tax_id': False})


        return res

    #GAP V1 : Do not allow write when different rebu products in lines
    def write(self, values):
        result = super().write(values)

        if 'is_rebu' in values:
            for r in self:
                if r.is_rebu:
                    r.order_line.write({'tax_id': False})

                else:
                    for l in r.order_line:
                        if l.product_id and l.product_id.taxes_id:
                            l.write({'tax_id': l.product_id.taxes_id.ids})
                        else:
                            l.write({'tax_id': False})

        return result