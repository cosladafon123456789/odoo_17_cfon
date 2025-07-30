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
import odoo
from odoo import http, _
from odoo.http import request
import urllib.parse as urlparse

import logging
_logger = logging.getLogger(__name__)

class PaypalExpressRedirect(http.Controller):

    def search_partner_address(self, address, type, partner_id=None):
        partnerAddress = request.env['res.partner'].sudo()
        domain = [
            ('name','=',address['name']),
            ('email','=',address['email']),
            ('phone','=',address['phone']),
            ('type','=',type),
            ('street','=',address['street']),
            ('street2','=',address['street2']),
            ('city','=',address['city']),
            ('zip','=',address['zip']),
            ('state_id','=',address['state_id']),
            ('country_id','=',address['country_id']),
        ]
        if partner_id:
            domain+= [('parent_id','=',partner_id)]
        address = partnerAddress.search(domain, limit=1)
        return address

    def create_partner_address(self, address, type, partner_id=None):
        partnerAddress = request.env['res.partner'].sudo()
        vals = {
            'name' : address['name'],
            'email' : address['email'],
            'phone' : address['phone'],
            'type' : type,
            'street' : address['street'],
            'street2' : address['street2'],
            'city' : address['city'],
            'state_id' : address['state_id'],
            'zip' : address['zip'],
            'country_id' : address['country_id'],
        }
        if partner_id:
            vals['parent_id'] = partner_id
        address = partnerAddress.create(vals)
        return address

    def update_addresses_from_paypal(self, sale_order, trans_obj, billing, shipping):
        so_updates, trans_updates = {}, {}
        public_partner_id = request.website.partner_id.id
        partner = request.env.user.partner_id
        acquirer_obj = trans_obj.provider_id if trans_obj else None
        if not acquirer_obj:
            acquirer_obj = request.env['payment.provider'].sudo().search([('code','=','paypal_express'),'|', ('website_id', '=', False), ('website_id', '=', request.website.id)], limit=1)

        if partner.id != public_partner_id:
            if acquirer_obj.override_billing:
                address = self.search_partner_address(billing, 'invoice', partner.id)
                if not address:
                    address = self.create_partner_address(billing, 'invoice', partner.id)
                if sale_order.partner_invoice_id.id != address.id:
                    so_updates['partner_invoice_id'] = address.id
                if trans_obj and trans_obj.partner_id.id == public_partner_id:
                    trans_updates['partner_id'] = address.id
            if acquirer_obj.override_shipping:
                address = self.search_partner_address(shipping, 'delivery', partner.id)
                if not address:
                    address = self.create_partner_address(shipping, 'delivery', partner.id)
                if sale_order.partner_shipping_id.id != address.id:
                    so_updates['partner_shipping_id'] = address.id
        else:
            so_partner = request.website.sale_get_order().partner_id
            if not so_partner.is_public: 
                if acquirer_obj.override_billing:
                    contact_address = self.search_partner_address(billing, 'contact')
                    if not contact_address:
                        contact_address = self.create_partner_address(billing, 'invoice', so_partner.id)
                        so_updates['partner_invoice_id'] = contact_address.id
                        trans_updates['partner_id'] = contact_address.id
                if acquirer_obj.override_shipping:
                    delivery_address = self.search_partner_address(shipping, 'delivery', so_partner.id)
                    if not delivery_address:
                        delivery_address = self.create_partner_address(shipping, 'delivery', so_partner.id)
                        so_updates['partner_shipping_id'] = delivery_address.id
            else:
                # Here iam managing case when we express checkout
                contact_address = self.search_partner_address(billing, 'contact')
                if not contact_address:
                    contact_address = self.create_partner_address(billing, 'invoice')
                    so_updates['partner_invoice_id'] = contact_address.id
                    so_updates['partner_id'] = contact_address.id
                    trans_updates['partner_id'] = contact_address.id
                delivery_address = self.search_partner_address(shipping, 'delivery', contact_address.id)
                if not delivery_address:
                    delivery_address = self.create_partner_address(shipping, 'delivery', contact_address.id)
                    so_updates['partner_shipping_id'] = delivery_address.id
        if so_updates:
            sale_order.sudo().write(so_updates)
        if trans_obj and trans_updates:
            trans_obj.sudo().write(trans_updates)

    def get_address_format(self, address):
        country_id = request.env['res.country'].sudo().search([('code','=',address.get('country_code'))], limit=1)
        country_id = country_id.id if country_id else None
        s_state = address.get('admin_area_1')
        state = request.env['res.country.state'].sudo().search(['|',('code','=',s_state),('name','=ilike',s_state),('country_id','=',country_id)], limit=1)
        state_id = state.id if state else None
        return {
            'street': address.get('address_line_1'),
            'street2': address.get('address_line_2'),
            'city': address.get('admin_area_2'),
            'zip': address.get('postal_code'),
            'state_id': state_id,
            'country_id': country_id
        }

    @http.route(['/paypal/express/checkout/url',], type='json', auth="public", methods=['POST'], website=True)
    def paypal_checkout_checkout_url(self, **post):
        pricelist = request.session.get('website_sale_current_pl')
        acquirer_obj = request.env['payment.provider'].sudo().search([('code','=','paypal_express'),'|', ('website_id', '=', False), ('website_id', '=', request.website.id)], limit=1)
        if acquirer_obj:
            url = "https://www.paypal.com/sdk/js?"
            if acquirer_obj.disable_funding:
                url += 'disable-funding='+ str(acquirer_obj.disable_funding)
                url += "&client-id=" + str(acquirer_obj.paypal_client_id)
            else:
                url += "client-id=" + str(acquirer_obj.paypal_client_id)
            lang = request.lang
            web_url = request.httprequest.environ.get('HTTP_REFERER')
            path = urlparse.urlparse(web_url).path if web_url else None
            path_query = urlparse.urlparse(web_url).query
            so_id = None
            curr_obj = None
            if path and "/my/orders/" in path and len(path) > 11 and path.split("/")[-1].isdigit():
                so_id = int(path.split("/")[-1])


            elif path_query and 'sale_order_id' in path_query:
                path_query_list = path_query.split("&")
                for rec in path_query_list:
                    if 'sale_order_id' in rec:
                        order_id = rec.split('sale_order_id=')
                        if len(order_id) >1:
                            so_id = int(order_id[1])
                            break

            sale_order_obj = request.env['sale.order'].sudo()

            if so_id:
                pricelist = sale_order_obj.search([("id","=",so_id)]).pricelist_id
                if pricelist:
                    pricelist = pricelist.id

            elif request.session.get('sale_order_id'):
                pricelist = sale_order_obj.search([("id","=",request.session.get('sale_order_id'))]).pricelist_id
                if pricelist:
                    pricelist = pricelist.id

            if path and "/my/invoices/" in path and len(path) > 12 and path.split("/")[-1].isdigit():
                if int(path.split('/')[-1]):
                    inv_obj = request.env['account.move'].sudo().browse(int(path.split('/')[-1]))
                    if inv_obj.currency_id:
                        curr_obj = inv_obj.currency_id
                        pricelist = None

            if pricelist:
                pricelist = request.env['product.pricelist'].browse(pricelist)
                if pricelist and pricelist.currency_id:
                    curr_obj = pricelist.currency_id

            elif path_query and 'currency_id' in path_query:
                path_query_list = path_query.split("&")
                for rec in path_query_list:
                    if 'currency_id' in rec:
                        currency_id = rec.split('currency_id=')
                        if len(currency_id) >1:
                            curr_obj = request.env['res.currency'].sudo().browse(int(currency_id[1]))
                            break
            if not curr_obj and request.website:
                curr_obj = request.website.currency_id
            if curr_obj:
                url += '&currency=' + str(curr_obj.name)
            if lang:
                url += '&locale=' + str(lang.code)
            url += '&commit=false' 
            return url
        return False

    @http.route(['/paypal/express/checkout/state',], type='json', auth="public", methods=['POST'], website=True)
    def paypal_checkout_checkout_state(self, **post):
        shipping_address = {}
        billing_address = {}
        try:
            purchase_units = post.get('purchase_units')
            payer = post.get('payer')
            phone_numbers = payer['phone']['phone_number']['national_number'] if payer and payer.get('phone') else None
            email_address = payer['email_address']
            # Get billing address details
            billing_address = payer.get('address')
            billing_address = self.get_address_format(billing_address)
            payer_name = payer['name'].get('given_name','')+ ' ' +payer['name'].get('surname','')
            billing_address.update({
                'address_type': 'invoice',
                'email': email_address,
                'phone': phone_numbers,
                'name': payer_name
            })

            # Get shipping address details
            shipping_address = purchase_units[0]['shipping']['address']
            shipping_address = self.get_address_format(shipping_address)
            recipient_name = purchase_units[0]['shipping']['name']['full_name']
            shipping_address.update({
                'address_type': 'delivery',
                'email': email_address,
                'phone': phone_numbers,
                'name': recipient_name
            })
        except Exception as e:
            _logger.info("~~~~~~~~~~~~~Exception~~~~~~~~%r~~~~~~~~~~~~~~~",e)
        order = request.website.sale_get_order()
        if order:
            trans_id = request.session.get('sale_transaction_id',False)
            if not trans_id:
                trans_obj = order.sudo().transaction_ids._get_last()
            else:
                trans_obj = request.env['payment.transaction'].sudo().browse(int(trans_id))
            self.update_addresses_from_paypal(order, trans_obj, billing_address, shipping_address)
            request.session['sale_last_order_id'] = order.id

        purchase_units = post.get('purchase_units')
        data = {}
        try:
            if purchase_units:
                purchase_units = purchase_units[0]
                data['invoice_num'] = purchase_units['reference_id']
                captures = purchase_units['payments']['captures']
                if captures:
                    captures = captures[0]
                    data['provider_reference'] = captures['id']
                    data['state'] = captures['status']
                    data['amount'] = captures['amount']['value']
                    data['currency'] = captures['amount']['currency_code']
        except Exception as e:
            _logger.info("~~~~~~~~~~~~~~EXCEPTION~~~~~~~~~~~%r~~~~~~~~~~~~~~~",e)
        notification_data = data
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data('paypal_express', notification_data)
        tx_sudo._handle_notification_data('paypal_express', notification_data)
        return '/payment/status'

    @http.route(['/paypal/express/checkout/cancel'], type='json', auth="public", methods=['POST'], website=True)
    def paypal_checkout_checkout_cancel(self, **post):
        trans_id = request.session.get('__website_sale_last_tx_id',False)
        web_url = request.httprequest.environ.get('HTTP_REFERER')
        path = urlparse.urlparse(web_url).path if web_url else '/payment/status'
        path_query = urlparse.urlparse(web_url).query

        if trans_id:
            trans_obj = request.env['payment.transaction'].sudo().browse(int(trans_id)) if trans_id else None
            try:
                trans_obj._set_canceled()
            except Exception as e:
                _logger.info("~~~~~~~~Transaction already in process~~~~~~~~~")
        if path_query:
            path = path +'?'+path_query
        return path

    @http.route(['/paypal/express/checkout/error'], type='json', auth="public", methods=['POST'], website=True)
    def paypal_checkout_checkout_error(self, **post):
        error_msg = post.get('error',None)
        trans_id = request.session.get('__website_sale_last_tx_id',False)
        if trans_id and error_msg:
            trans_obj = request.env['payment.transaction'].sudo().browse(int(trans_id)) if trans_id else None
            try:
                trans_obj._set_error(error_msg)
            except Exception as e:
                _logger.info("~~~~~~~~Transaction already in process~~~~~~~~~")
        return '/payment/status'
