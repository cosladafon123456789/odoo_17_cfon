from odoo import models

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _check_expiration_date(self):
        """
        Cortocircuitamos la comprobación a nivel de línea, cuando exista.
        """
        return True