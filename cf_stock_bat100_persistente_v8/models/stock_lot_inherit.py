from odoo import models, fields, api

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    bat100 = fields.Boolean(
        string='BAT100',
        tracking=True,
        readonly=False,
        store=True,
    )
