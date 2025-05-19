from odoo import models, fields, api, _


class SendCloudIntegration(models.Model):
    _name = "sendcloud.integration"
    _description = "SendCloud Integrations"

    name = fields.Char("Name", required=True)
    sendcloud_id = fields.Char("ID", required=True, copy=False, readonly=True)
    service_point_enabled = fields.Boolean(" Service Points", copy=False,
                                           help="Enable the service point picker to be shown in the checkout of your store. For more information, please refer to the manual.")
    service_point_carrier_ids = fields.Many2many('sendcloud.carrier', 'sendcloud_int_carrier_rel', 'integration_id', 'carrier_id', string='Carriers',
                                                 help="Carrier which has service points enabled")

    def fetch_from_sendcloud(self):
        self.ensure_one()
        shipping_partner = self.env['shipping.partner'].search([('sendcloud_integration_id', '=', self.id)])
        if shipping_partner and self.sendcloud_id:
            response = shipping_partner._sendcloud_send_request('integrations', {})
            for integration in response:
                if integration.get('id') != int(self.sendcloud_id):
                    continue
                created_or_updated_carriers = shipping_partner._sendcloud_create_or_update_carrier(integration.get('service_point_carriers'))
                service_point_carriers_ids = created_or_updated_carriers and created_or_updated_carriers.ids or []
                vals = {'sendcloud_id': integration.get('id'), 'name': integration.get('shop_name'), 'service_point_enabled': integration.get('service_point_enabled'),
                        'service_point_carrier_ids': [(6, 0, service_point_carriers_ids)]}
                self.write(vals)
                break
        return True

    def _update_in_sendcloud(self):
        shipping_partner = self.env['shipping.partner'].search([('sendcloud_integration_id', '=', self.id)])
        if shipping_partner and self.sendcloud_id:
            carriers = self.service_point_carrier_ids.mapped('name')
            response = shipping_partner._sendcloud_send_request('integrations/%s' % self.sendcloud_id,{'shop_name': self.name, 'service_point_enabled': self.service_point_enabled, 'service_point_carriers': carriers},method="PUT")
        return True

    def write(self, vals):
        res = super(SendCloudIntegration, self).write(vals)
        self._update_in_sendcloud()
        return res
