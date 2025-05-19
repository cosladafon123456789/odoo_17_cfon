from odoo import fields, models,api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sendcloud_tracking_url = fields.Char("SendCloud Tracking URL", copy=False)
    sendcloud_parcel_ids = fields.Char("SendCloud Parcel IDs", copy=False)
    sb_service_point_details = fields.Text('Service Point Details', help='Address of service point.',copy=False)
    is_enable_service_point = fields.Boolean('Enable Service Point',readonly=True, related="carrier_id.is_enable_service_point")
    sender_address_id = fields.Many2one('sender.address', string="Ship From(Sendcloud)")


    def get_details_sendcloud_backend(self):
        self.ensure_one()
        res = {'is_sendcloud_service_point_enable':False}
        self.write({'sb_service_point_details':False})
        if self.carrier_id and self.carrier_id.shipping_partner_id:
            shipping_partner = self.carrier_id.shipping_partner_id
            if self.carrier_id and self.carrier_id.delivery_type == 'sendcloud_ts' and shipping_partner:
                public_key = shipping_partner.sendcloud_public_key or ''
                carrier_name = self.carrier_id.sendcloud_service_id and self.carrier_id.sendcloud_service_id.carrier_id.name or ''
                country_code = self.partner_id and self.partner_id.country_id and self.partner_id.country_id.code or ''
                zip_code = self.partner_id and self.partner_id.zip or ''
                res.update({'order_id' : self.id,
                            'key':public_key,
                            'country_code':country_code,
                            'postcode':zip_code,
                            'carrier_name':[carrier_name]
                })
        return res
