from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    street_no = fields.Char(string='House No.')
