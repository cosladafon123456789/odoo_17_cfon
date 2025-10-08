from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    web_url = fields.Char(string="API URL")
    web_token = fields.Char(string="Access Token")
