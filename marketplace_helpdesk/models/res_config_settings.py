from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    marketplace_account_ids = fields.One2many(related="company_id.marketplace_account_ids", readonly=False)
