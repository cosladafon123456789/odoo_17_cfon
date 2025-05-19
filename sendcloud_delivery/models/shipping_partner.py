import json
import requests
import base64
from odoo import tools
from odoo import models, fields, api, _
from requests.auth import HTTPBasicAuth
from odoo.tools import file_path
from odoo.exceptions import UserError, ValidationError


class ShippingPartner(models.Model):
    _inherit = "shipping.partner"

    provider_company = fields.Selection(selection_add=[('sendcloud_ts', 'SendCloud')])
    sendcloud_public_key = fields.Char("Public Key", copy=False)
    sendcloud_secret_key = fields.Char("Secret Key", copy=False)
    sendcloud_integration_id = fields.Many2one("sendcloud.integration", string="Integration")

    def get_sendcloud_sender_address(self):
        sender_address_obj = self.env['sender.address']
        if self.provider_company == 'sendcloud_ts' and self.sendcloud_public_key and self.sendcloud_secret_key:
            response = self._sendcloud_send_request('user/addresses/sender', {})
            sender_addresses = response.get('sender_addresses')
            for sender_address in sender_addresses:
                sender_address_id = sender_address_obj.search([('address_id', '=', sender_address.get('id'))], limit=1)
                if not sender_address_id:
                    sender_address_obj.create({'address_id': sender_address.get('id'), 'name': sender_address.get('company_name'),
                                               'contact_name': sender_address.get('contact_name'), 'email': sender_address.get('email'),
                                               'telephone': sender_address.get('telephone'),
                                               'street': sender_address.get('street'), 'house_number': sender_address.get('house_number'),
                                               'postal_code': sender_address.get('postal_code'), 'city': sender_address.get('city'),
                                               'country': sender_address.get('country'), 'vat_number': sender_address.get('vat_number'),
                                               'eori_number': sender_address.get('eori_number'), 'shipping_partner_id': self.id})
                else:
                    sender_address_id.write({'name': sender_address.get('company_name'), 'contact_name': sender_address.get('contact_name'),
                                             'email': sender_address.get('email'), 'telephone': sender_address.get('telephone'),
                                             'street': sender_address.get('street'), 'house_number': sender_address.get('house_number'),
                                             'postal_code': sender_address.get('postal_code'), 'city': sender_address.get('city'),
                                             'country': sender_address.get('country'), 'vat_number': sender_address.get('vat_number'),
                                             'eori_number': sender_address.get('eori_number'), 'shipping_partner_id': self.id})
        else:
            raise UserError('An API credentials required to get your SendCloud carriers.')
        return True

    @api.model
    def _sendcloud_send_request(self, request_url, request_data, prod_environment=True, params=False, method='GET'):
        headers = {
            'Content-Type': 'application/json',
        }
        if prod_environment:
            api_url = 'https://panel.sendcloud.sc/api/v2/' + request_url
        else:
            raise UserError("Sandbox/Testing environment is not supported by SendCloud.")
        try:
            if request_data:
                req = requests.request(method, api_url,
                                       auth=HTTPBasicAuth(self.sendcloud_public_key, self.sendcloud_secret_key),
                                       headers=headers, params=params,
                                       json=request_data)
            else:
                req = requests.request(method, api_url,
                                       auth=HTTPBasicAuth(self.sendcloud_public_key, self.sendcloud_secret_key),
                                       headers=headers, params=params)
            req.raise_for_status()
            if isinstance(req.content, bytes):
                req = req.content.decode("utf-8")
                response = json.loads(req)
            else:
                response = json.loads(req.content)
        except requests.HTTPError as e:
            response = json.loads(req.text)
            if response.get('error', False):
                error_msg = response.get('error', {}).get('message', False)
                raise UserError(_("SendCloud: %s" % error_msg or req.text))
            raise UserError(_("SendCloud: %s" % e))
        return response

    def get_sendcloud_carriers(self):
        service_obj = self.env['sendcloud.service']
        res_country_obj = self.env['res.country']
        if self.provider_company == 'sendcloud_ts' and self.sendcloud_public_key and self.sendcloud_secret_key:
            response = self._sendcloud_send_request('shipping_methods', {}, params={'sender_address': "all"})
            carriers = response.get('shipping_methods')
            for carrier in carriers:
                existing = service_obj.search([('sendcloud_id', '=', carrier.get('id'))])
                service_country_vals = []
                for country in carrier.get('countries'):
                    country_id = res_country_obj.search([('code', '=', country.get('iso_2'))])
                    service_country_vals.append((0, 0, {
                        'country_id': country_id.id,
                        'price': country.get('price'),
                    }))
                carrier_id = False
                if carrier.get('carrier'):
                    carrier_id = self._sendcloud_create_or_update_carrier(carrier.get('carrier'))
                vals = {'sendcloud_id': carrier.get('id'), 'name': carrier.get('name'), 'carrier_id': carrier_id and carrier_id.id or False, 'max_weight': carrier.get('max_weight'),
                        'service_country_ids': service_country_vals}
                if existing:
                    existing.service_country_ids.unlink()
                    existing.write(vals)
                    continue
                service_obj.create(vals)
        else:
            raise UserError('An API credentials required to get your SendCloud carriers.')

    def _sendcloud_create_or_update_carrier(self, carriers):
        carrier_obj = self.env['sendcloud.carrier']
        created_or_updated_carriers = self.env['sendcloud.carrier']
        if not carriers:
            return False
        if not isinstance(carriers, list):
            carriers = [carriers]
        for carrier in carriers:
            existing = carrier_obj.search([('name', '=', carrier)])
            if existing:
                created_or_updated_carriers |= existing
                continue
            created_or_updated_carriers |= carrier_obj.create({'name': carrier})
        return created_or_updated_carriers

    def get_sendcloud_integration_details(self):
        integration_obj = self.env['sendcloud.integration']
        if self.provider_company == 'sendcloud_ts' and self.sendcloud_public_key and self.sendcloud_secret_key:
            response = self._sendcloud_send_request('integrations', {})
            for integration in response:
                if integration.get('system') != 'api':
                    continue
                existing = integration_obj.search([('sendcloud_id', '=', integration.get('id'))])
                created_or_updated_carriers = self._sendcloud_create_or_update_carrier(integration.get('service_point_carriers'))
                service_point_carriers_ids = created_or_updated_carriers and created_or_updated_carriers.ids or []
                vals = {'sendcloud_id': integration.get('id'), 'name': integration.get('shop_name'), 'service_point_enabled': integration.get('service_point_enabled'),
                        'service_point_carrier_ids': [(6, 0, service_point_carriers_ids)]}
                if existing:
                    existing.write(vals)
                    continue
                integration_obj.create(vals)
            self.get_sendcloud_carriers()
        else:
            raise UserError('An API credentials required to get your SendCloud integration details.')

    @api.onchange('provider_company')
    def _onchange_provider_company(self):
        res = super(ShippingPartner, self)._onchange_provider_company()
        if self.provider_company == 'sendcloud_ts':
            image_path = file_path('sendcloud_delivery/static/description/icon.png')
            self.image = base64.b64encode(open(image_path, 'rb').read())
        return res
