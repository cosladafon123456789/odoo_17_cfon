from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    marketplace_account_ids = fields.One2many(
        'marketplace.account',
        'config_id',
        string='Cuentas de Marketplaces'
    )
