from odoo import fields, models

class MarketplaceAccount(models.Model):
    _name = "marketplace.account"
    _description = "Cuenta de Marketplace"
    _order = "name"

    name = fields.Char(string="Nombre de la cuenta", required=True)
    api_url = fields.Char(string="URL de la API")
    api_key = fields.Char(string="API Key")
    active = fields.Boolean(string="Activo", default=True)
