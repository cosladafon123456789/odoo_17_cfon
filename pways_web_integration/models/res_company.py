from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    web_url = fields.Char(string="API URL", required=True)
    web_token = fields.Char(string="Access Token", required=True)
