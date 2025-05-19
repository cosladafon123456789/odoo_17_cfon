# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

import logging
_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    #GAP V1
    is_rebu = fields.Boolean(string=_("Is REBU"), default=False)

    #GAP V1
    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for r in res:
            if r.is_rebu:
                for l in r.order_line:
                    if l.product_id and l.product_id.rebu_tax_id:
                        l.write({'taxes_id': l.product_id.rebu_tax_id.ids})
                    else:
                        l.write({'taxes_id': False})

        return res

    #GAP V1 : Do not allow write when different rebu products in lines
    def write(self, values):
        result = super().write(values)

        if 'is_rebu' in values:
            for r in self:
                if r.is_rebu:
                    for l in r.order_line:
                        if l.product_id and l.product_id.rebu_tax_id:
                            l.write({'taxes_id': l.product_id.rebu_tax_id.ids})
                        else:
                            l.write({'taxes_id': False})
                else:
                    for l in r.order_line:
                        if l.product_id and l.product_id.taxes_id:
                            l.write({'taxes_id': l.product_id.taxes_id.ids})
                        else:
                            l.write({'taxes_id': False})

        return result
   

    #GAP V1
    def _prepare_invoice(self):
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        if self.is_rebu:
            invoice_vals.update({'is_rebu': True})
        return invoice_vals
    
    #GAP V1
    def action_create_invoice(self):
        rebu_orders = self.filtered(lambda x: x.is_rebu == True)
        not_rebu_orders = self - rebu_orders

        if rebu_orders and not_rebu_orders:
            raise UserError(_("Cannot create invoice from REBU and not REBU orders"))
        
        return super(PurchaseOrder, self).action_create_invoice()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    #GAP V1
    lot_price_assigned = fields.Boolean(string=_("Lot price is assigned"), default=False)
    is_rebu = fields.Boolean(string=_("Is REBU"), default=False)
    