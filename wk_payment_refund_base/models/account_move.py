# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################

from odoo import models, fields, _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_refunded = fields.Boolean(string="Refunded")

    def _get_transaction(self, provider_code):
        """
            Retrieves a successful transaction for the given provider.

            This method retrieves a transaction related to the current record
            (which is assumed to be an invoice or credit note).  It handles
            different scenarios based on the document type and the availability
            of transaction IDs.

            Args:
                provider_code (str): The code of the payment provider.

            Returns:
                recordset: A filtered recordset of transactions that match the provider
                        code and are in the 'done' state.  May be empty.
        """
        self.ensure_one()
        if self.move_type == 'out_refund':
            if not self.reversed_entry_id:
                raise ValidationError(_("Missing: Source invoice record."))
            self = self.reversed_entry_id
        if self.transaction_ids:
            return self.transaction_ids.filtered(lambda transaction: transaction.provider_code == provider_code and transaction.state == 'done')
        else:
            sale_order = self.line_ids.sale_line_ids.order_id
            return sale_order.transaction_ids.filtered(lambda transaction: transaction.provider_code == provider_code and transaction.state == 'done')

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    wk_refund_reason = fields.Char(string="Refund Reason")
