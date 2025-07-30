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
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.payment import utils as payment_utils
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError
import pprint
import logging
_logger = logging.getLogger(__name__)
PAYPAL_BUTTON_TEMPLATES = ['payment_paypal_express.inherit_payment_submit_button']

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('paypal_express', 'Paypal Checkout')],ondelete={'paypal_express': 'cascade'})
    paypal_client_id = fields.Char("Paypal Client ID", required_if_provider='paypal_express', help="Enter paypal client ID.")
    override_shipping = fields.Boolean("Update Shipping Details")
    override_billing = fields.Boolean("Update Billing Details")
    disable_funding = fields.Char("Disable funding", help="Any funding sources that you pass aren't displayed as buttons at checkout.")

    @api.onchange('disable_funding')
    def _onchange_disable_funding(self):
        disable_funding_list = ['card','credit','paylater','bancontact','blik','eps','giropay','ideal','mercadopago','mybank','p24','sepa','sofort','venmo']
        if self.disable_funding and self.disable_funding!="" :
            value_disable_funding = self.disable_funding.split(',')
            for val in value_disable_funding:
                if val not in disable_funding_list:
                    raise UserError(_("{} is not a valid value for disable funding.".format(val)))

class TransactionPaypalExpress(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        rec = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'paypal_express':
            return rec
        if self.sale_order_ids:
            sale_order = self.sale_order_ids[0]
            rec['so_reference'] = sale_order.name
            billing_partner = sale_order.partner_invoice_id
            if billing_partner:
                first_name, last_name = payment_utils.split_partner_name(billing_partner.name)
                phone_no = ''.join(e for e in str(billing_partner.phone) if e.isalnum())
                rec.update({
                    'billing_first_name': first_name,
                    'billing_last_name': last_name,
                    'billing_phone': phone_no,
                    'billing_email': billing_partner.email,
                    'billing_address_l1': payment_utils.format_partner_address(
                        billing_partner.street, billing_partner.street2
                    ),
                    'billing_area1': billing_partner.state_id.code,
                    'billing_area2': billing_partner.city,
                    'billing_zip_code': billing_partner.zip,
                    'billing_country_code': billing_partner.country_id.code
                })
            shipping_partner = sale_order.partner_shipping_id
            if shipping_partner:
                rec.update({
                    'shipping_partner_name': shipping_partner.name,
                    'shipping_address_l1': payment_utils.format_partner_address(
                        shipping_partner.street, shipping_partner.street2
                    ),
                    'shipping_area1': shipping_partner.state_id.code,
                    'shipping_area2': shipping_partner.city,
                    'shipping_zip_code': shipping_partner.zip,
                    'shipping_country_code': shipping_partner.country_id.code
                })
        else:
            first_name, last_name = payment_utils.split_partner_name(self.partner_name)
            phone_no = ''.join(e for e in str(self.partner_phone) if e.isalnum())
            rec.update({
                'billing_first_name': first_name,
                'billing_last_name': last_name,
                'billing_phone': phone_no,
                'billing_email': self.partner_email,
                'billing_address_l1': self.partner_address,
                'billing_area1': self.partner_state_id.code,
                'billing_area2': self.partner_city,
                'billing_zip_code': self.partner_zip,
                'billing_country_code': self.partner_country_id.code
            })
        rec.update(processing_values)
        rec["currency_code"] = self.currency_id.name

        return rec

    @api.model
    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Given a data dict coming from paypal, verify it and find the related
        transaction record. Create a payment method if an alias is returned."""
        res = super()._get_tx_from_notification_data(provider_code,notification_data)
        if provider_code != "paypal_express":
            return res
        reference, amount, currency_name = notification_data.get('invoice_num'), notification_data.get('amount'), notification_data.get('currency')
        tx_ids = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not tx_ids or len(tx_ids) > 1:
            error_msg = 'received data for reference %s' % (pprint.pformat(reference))
            if not tx_ids:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return tx_ids[0]

    def _process_notification_data(self, notification_data):
        res = super()._process_notification_data(notification_data)
        if self.provider_code != "paypal_express":
            return res
        invalid_parameters = []
        # check what is buyed
        if float_compare(float(notification_data.get('amount', '0.0')), self.amount, 2) != 0:
            invalid_parameters.append(('Amount', notification_data.get('amount'), '%.2f' % self.amount))
        if notification_data.get('currency') != self.currency_id.name:
            invalid_parameters.append(('Currency', notification_data.get('currency'), self.currency_id.name))
        if invalid_parameters:
            raise ValidationError(_(
                "Received data is not matched with any transaction such as %r", ",".join([i[0] for i in invalid_parameters])))
        else:
            trans_state = notification_data.get("state", False)
            if trans_state:
                self.write({
                    'provider_reference':notification_data.get('provider_reference'),
                    'state_message': _("Paypal Payment Gateway Response :-") + notification_data["state"]
                })
                if trans_state == 'COMPLETED':
                    self._set_done()
                elif trans_state == "PENDING":
                    self._set_pending()
                elif trans_state == "DECLINED":
                    self._set_canceled()
                # elif trans_state == "PARTIALLY_REFUNDED":
                # elif trans_state == "REFUNDED":


class PaypalButtonView(models.Model):

    _inherit = 'ir.ui.view'

    def save(self, value, xpath=None):
        self.ensure_one()
        if not self.exists() or self.key not in PAYPAL_BUTTON_TEMPLATES:
            super().save(value, xpath=xpath)