from odoo import fields, models

class MarketplaceAccount(models.Model):
    _name = 'marketplace.account'
    _description = 'Cuenta de Marketplace'

    name = fields.Char(string='Nombre de la cuenta', required=True)
    api_url = fields.Char(string='URL de la API', required=True)
    api_key = fields.Char(string='API Key', required=True)
    active = fields.Boolean(string='Activo', default=True)

    # Relación inversa con los ajustes
    config_id = fields.Many2one('res.config.settings', string='Configuración')
