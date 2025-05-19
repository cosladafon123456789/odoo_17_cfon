from odoo import models, fields, api, _


class SendCloudSarrier(models.Model):
    _name = "sendcloud.service"
    _description = "SendCloud Service"

    name = fields.Char("Name", required=True)
    sendcloud_id = fields.Char("ID", required=True, copy=False, readonly=True)
    max_weight = fields.Float("Max Weight", copy=False)
    carrier_id = fields.Many2one("sendcloud.carrier", string="Carrier")
    service_country_ids = fields.One2many("sendcloud.service.country", "service_id", "Available Countries")


class SendCloudServiceCountries(models.Model):
    _name = "sendcloud.service.country"
    _description = "SendCloud Services Countries"

    country_id = fields.Many2one("res.country", string="Country")
    price = fields.Float("Price", readonly=True)
    service_id = fields.Many2one("sendcloud.service", string="Service", ondelete="cascade")
