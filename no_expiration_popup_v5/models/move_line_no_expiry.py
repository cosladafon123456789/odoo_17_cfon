from odoo import models

class StockMoveLineNoExpiry(models.Model):
    _inherit = "stock.move.line"

    def _check_expiration_date(self):
        # Evita que cualquier comprobación a nivel de línea dispare el wizard
        return True
