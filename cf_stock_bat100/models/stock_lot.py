from odoo import models, fields

class StockLot(models.Model):
    _inherit = "stock.lot"

    bat100 = fields.Boolean(string="BAT100", help="Indica si el dispositivo tiene la batería al 100%.")