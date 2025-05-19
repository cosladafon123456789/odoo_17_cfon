import json
import logging
import requests
from markupsafe import Markup
from odoo import models, fields, api, tools, _
from requests.auth import HTTPBasicAuth
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('sendcloud_ts', "SendCloud")], ondelete={'sendcloud_ts': 'cascade'})
    sendcloud_service_id = fields.Many2one('sendcloud.service', "Service")
    sendcloud_delivery_type = fields.Selection([('domestic', 'Domestic'), ('international', 'International')], default="domestic", string="Delivery Type")
    sendcloud_shipment_type = fields.Selection([('0', 'Gift'), ('1', 'Documents'), ('2', 'Commercial Goods'), ('3', 'Commercial Sample'), ('4', 'Returned Goods')], default='2', string="Shipment Type")
    sendcloud_apply_shipping_rules = fields.Boolean("Apply Shipping Rules?", default=True, help="When set to True configured shipping rules will be applied before creating the label and announcing the Parcel")
    is_enable_service_point = fields.Boolean('Enable Service Point', compute='_compute_is_enable_service_point', store=True)

    @api.depends('sendcloud_service_id', 'shipping_partner_id.sendcloud_integration_id.service_point_carrier_ids')
    def _compute_is_enable_service_point(self):
        for record in self:
            if record.delivery_type == 'sendcloud_ts':
                if record.sendcloud_service_id.carrier_id.name in record.shipping_partner_id.sendcloud_integration_id.service_point_carrier_ids.mapped('name') and record.shipping_partner_id.sendcloud_integration_id.service_point_enabled:
                    record.is_enable_service_point = True
            else:
                record.is_enable_service_point = False

    @api.onchange('sendcloud_service_id')
    def _onchange_sendcloud_service(self):
        if self.delivery_type == 'sendcloud_ts' and self.sendcloud_service_id:
            if self.sendcloud_service_id.service_country_ids:
                self.country_ids = self.sendcloud_service_id.service_country_ids.mapped('country_id')
        elif self.delivery_type == 'sendcloud_ts' and not self.sendcloud_service_id:
            self.country_ids = False

    def sendcloud_ts_service_point_enabled(self):
        self.ensure_one()
        if not self.shipping_partner_id:
            return False
        elif self.shipping_partner_id and not self.shipping_partner_id.sendcloud_integration_id:
            return False
        self.shipping_partner_id.sendcloud_integration_id.fetch_from_sendcloud()
        if self.sendcloud_service_id.carrier_id.name in self.shipping_partner_id.sendcloud_integration_id.service_point_carrier_ids.mapped('name'):
            return True
        return False

    def _sendcloud_ts_convert_weight(self, weight):
        weight_uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        if self.env.ref('uom.product_uom_kgm').id != weight_uom_id.id:
            weight = weight_uom_id._compute_quantity(weight, self.env.ref('uom.product_uom_kgm'), round=False)
        return weight

    def sendcloud_ts_add_parcel(self, picking, recipient, weight):
        sender_address_id = picking.sender_address_id and picking.sender_address_id.address_id or False
        if not sender_address_id:
            sender_address = self.env['sender.address'].search([('shipping_partner_id', '=', self.shipping_partner_id.id)])
            if len(sender_address.mapped('id')) != 1:
                sender_address = self.env['sender.address'].search([('default_address', '=', True), ('shipping_partner_id', '=', self.shipping_partner_id.id)], limit=1)
            sender_address_id = sender_address and sender_address.address_id or False
        company_name = recipient.commercial_company_name or ''
        parcel_dict = {
            "name": recipient.name,
            "company_name": company_name,
            "address": recipient.street or '',
            "house_number": recipient.street_no or '',
            "address_2": recipient.street2 or '',
            "city": recipient.city or '',
            "postal_code": recipient.zip,
            "country_state": recipient.state_id.code or '',
            "telephone": recipient.phone or recipient.mobile or '',
            "request_label": True,
            "apply_shipping_rules": self.sendcloud_apply_shipping_rules,
            "email": recipient.email or '',
            "data": [],
            "country": recipient.country_id.code or '',
            "shipment": {
                "id": self.sendcloud_service_id.sendcloud_id,
            },
            "weight": self._sendcloud_ts_convert_weight(weight),
            "order_number": picking.sale_id and picking.sale_id.name or picking.name,
            "sender_address": sender_address_id or ''
        }
        if recipient.country_id.code in ('US', 'CA'):
            parcel_dict.update({'to_state': recipient.state_id.code})
        ##Added For service Point
        if picking.is_enable_service_point and picking.sb_service_point_details:
            service_point_data = json.loads(picking.sb_service_point_details)
            parcel_dict.update({'to_service_point': int(service_point_data.get('id', '')),
                                'to_post_number': service_point_data.get('postal_code', '')})
        return parcel_dict

    def sendcloud_ts_add_custom_data(self, picking, move_lines):
        customs_items = []
        invoice_numbers = []
        for line in move_lines:
            if line.product_id.type not in ['product', 'consu']:
                continue
            inv_nos = line.move_id.sale_line_id.invoice_lines.mapped('move_id').mapped('name')
            if not inv_nos:
                raise UserError(_("Invoice number needed to process international shipment. Invoice not found for product : %s." % line.product_id.name))
            invoice_numbers.extend(inv_nos)
            customs_items.append({
                'description': line.product_id.name,
                'quantity': line.quantity,
                'weight': self._sendcloud_ts_convert_weight(line.product_id.weight * line.quantity),
                'value': tools.float_round(line.product_id.list_price * line.quantity, precision_digits=2),
                'hs_code': line.product_id.hs_code or '',
                'origin_country': picking.picking_type_id.warehouse_id.partner_id.country_id.code,
            })
        return set(invoice_numbers), customs_items

    def sendcloud_ts_rate_shipment(self, order):
        recipient = order.partner_shipping_id
        est_weight_value = sum([(line.product_id.weight * line.product_uom_qty) for line in order.order_line.filtered(lambda x: not x.product_id.type in ['service', 'digital'])]) or 0.0
        est_weight_value = self._sendcloud_ts_convert_weight(est_weight_value)
        max_weight = self.sendcloud_service_id.max_weight
        total_package = int(est_weight_value / max_weight)
        last_package_weight = est_weight_value % max_weight
        if last_package_weight:
            total_package += 1
        if self.sendcloud_service_id.service_country_ids and recipient.country_id:
            price = self.sendcloud_service_id.service_country_ids.filtered(lambda x: x.country_id == recipient.country_id).price
            shipping_charge = price * total_package
            if order.currency_id.name != 'EUR':
                rate_currency = self.env['res.currency'].search([('name', '=', 'EUR')], limit=1)
                if rate_currency:
                    shipping_charge = rate_currency._convert(price, order.currency_id)
            return {'success': True, 'price': shipping_charge, 'error_message': False, 'warning_message': False}
        else:
            return {'success': False, 'price': 0.0, 'error_message': False, 'warning_message': False}

    def sendcloud_ts_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            exact_price = 0.0
            request_data = {}
            tracking_number_list = []
            tracking_urls = []
            parcel_ids = []
            attachments = []
            # order = picking.sale_id
            # company = order.company_id or picking.company_id or self.env.user.company_id
            europe_country_group = self.env.ref('base.europe')
            is_outside_eu_shipment = False
            if picking.partner_id.country_id.id not in europe_country_group.country_ids.ids:
                is_outside_eu_shipment = True
            total_bulk_weight = round(picking.weight_bulk, 3)
            try:
                package_list = []
                if picking.package_ids:
                    # Create all packages
                    for package in picking.package_ids:
                        parcel_dict = self.sendcloud_ts_add_parcel(picking, picking.partner_id, package.shipping_weight or package.weight)
                        if is_outside_eu_shipment:
                            invoice_numbers, parcel_items = self.sendcloud_ts_add_custom_data(picking, picking.move_line_ids.filtered(lambda x: x.result_package_id == package))
                            parcel_dict.update({'customs_shipment_type': self.sendcloud_shipment_type, 'customs_invoice_nr': ','.join(invoice_numbers), 'parcel_items': parcel_items})
                        package_list.append(parcel_dict)
                # Create one package with the rest (the content that is not in a package)
                if total_bulk_weight:
                    parcel_dict = self.sendcloud_ts_add_parcel(picking, picking.partner_id, total_bulk_weight)
                    if is_outside_eu_shipment:
                        invoice_numbers, parcel_items = self.sendcloud_ts_add_custom_data(picking, picking.move_line_ids)
                        parcel_dict.update({'customs_shipment_type': self.sendcloud_shipment_type, 'customs_invoice_nr': ','.join(invoice_numbers), 'parcel_items': parcel_items})
                    # total_value = sum([(line.product_uom_qty * line.product_id.list_price) for line in picking.move_lines])
                    # parcel_dict.update({'insured_value': total_value})
                    package_list.append(parcel_dict)
                if not picking.package_ids and not total_bulk_weight:
                    raise UserError(_("Please define weight for delivery order."))
                if len(package_list) > 1:
                    request_data['parcels'] = package_list
                else:
                    request_data['parcel'] = package_list[0]
                response = self.shipping_partner_id._sendcloud_send_request('parcels', request_data, self.prod_environment, method="POST")
                if len(package_list) > 1:
                    response_parcel_list = response.get('parcels')
                else:
                    response_parcel_list = response.get('parcel')

                if isinstance(response_parcel_list, dict):
                    response_parcel_list = [response_parcel_list]
                for parcel in response_parcel_list:
                    parcel_id = parcel.get('id')
                    tracking_number = parcel.get('tracking_number')
                    tracking_url = parcel.get('tracking_url')
                    label_url = parcel.get('label', {}).get('label_printer', False)
                    customs_declaration_url = parcel.get('customs_declaration', {}).get('normal_printer', False)
                    label_binary_data = requests.get(label_url, auth=HTTPBasicAuth(self.shipping_partner_id.sendcloud_public_key, self.shipping_partner_id.sendcloud_secret_key)).content
                    tracking_number_list.append(tracking_number)
                    tracking_url and tracking_urls.append([tracking_number, tracking_url])
                    parcel_id and parcel_ids.append(parcel_id)
                    attachments.append(('SendCloud-%s.%s' % (tracking_number, 'pdf'), label_binary_data))
                    if customs_declaration_url:
                        customs_declaration_binary_data = requests.get(customs_declaration_url, auth=HTTPBasicAuth(self.shipping_partner_id.sendcloud_public_key, self.shipping_partner_id.sendcloud_secret_key)).content
                        attachments.append(('SendCloud-CN23-%s.pdf' % (tracking_number), customs_declaration_binary_data))
                picking.write({'sendcloud_parcel_ids': parcel_ids, 'sendcloud_tracking_url': tracking_urls})
                msg = (_('<b>Shipment created!</b><br/><b>Tracking Numbers:</b> %s') % (','.join(tracking_number_list)))
                picking.message_post(body=Markup(msg), attachments=attachments)
            except Exception as e:
                raise UserError(e)
            res = res + [{'exact_price': exact_price, 'tracking_number': ",".join(tracking_number_list)}]
        return res

    def sendcloud_ts_get_tracking_link(self, picking):
        tracking_urls = safe_eval(picking.sendcloud_tracking_url)
        if len(tracking_urls) == 1:
            return tracking_urls[0][1]
        return json.dumps(tracking_urls)

    def sendcloud_ts_cancel_shipment(self, picking):
        parcel_ids = safe_eval(picking.sendcloud_parcel_ids)
        for id in parcel_ids:
            self.shipping_partner_id._sendcloud_send_request('parcels/%s/cancel' % id, self.prod_environment, method="POST")
        return True
