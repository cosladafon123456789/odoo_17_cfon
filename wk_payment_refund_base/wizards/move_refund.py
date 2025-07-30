# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import fields, models

class paymentMoveRefundWizard(models.TransientModel):
    _name = 'payment.move.refund.wizard'
    _description = 'Account move payment refund'

    invoice_id = fields.Many2one(
        string="Invoice",
        comodel_name='account.move',
        readonly=True,
        default=lambda self: self.env.context.get('active_id'))

    currency_id = fields.Many2one(
        string="Currency", related='invoice_id.currency_id')

    total_amount = fields.Monetary(
        string="Total Amount", related='invoice_id.amount_total')
    
    provider_code = fields.Char(string="Provider Code")

    journal_id = fields.Many2one(
        'account.journal',
        string="Payment Journal",
        domain="[('type', 'in', ('bank', 'cash'))]"
    )
    refund_reason = fields.Text("Refund reason")

    def base_refund_process(self):
        '''
        Handles refund process.
        '''
        tx = self.invoice_id._get_transaction(self.provider_code)
        if tx:
            return tx[0]
        return False
