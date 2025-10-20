
from odoo import fields, models

class ResUsers(models.Model):
    _inherit = "res.users"
    cf_is_tracked = fields.Boolean(string="CF: Incluir en ranking", default=True)
