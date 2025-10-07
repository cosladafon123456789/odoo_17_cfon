from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"
    marketplace_account_ids = fields.One2many("marketplace.account", "company_id", string="Cuentas de marketplace")
