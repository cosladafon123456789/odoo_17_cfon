from odoo import models, fields, api, _


class SendCloudCarrier(models.Model):
    _name = "sendcloud.carrier"
    _description = "SendCloud Carrier"

    name = fields.Char("Name", required=True)
