from odoo import models

class StockMoveLineNoExpiry(models.Model):
    _inherit = "stock.move.line"

    def _check_expiration_date(self):
        return True
