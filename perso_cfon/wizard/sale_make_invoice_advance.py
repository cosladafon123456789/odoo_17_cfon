# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import format_date, frozendict


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    #GAP V1
    def create_invoices(self):
        rebu_orders = self.sale_order_ids.filtered(lambda x: x.is_rebu == True)
        not_rebu_orders = self.sale_order_ids - rebu_orders
        is_rebu = False

        if rebu_orders and not_rebu_orders:
            raise UserError(_("Cannot create invoice from REBU and not REBU orders"))
        
        if rebu_orders:
            is_rebu = True
        self._check_amount_is_positive()
        invoices = self._create_invoices(self.sale_order_ids)
        if is_rebu:
            invoices.write({'is_rebu': True})
        return self.sale_order_ids.action_view_invoice(invoices=invoices)