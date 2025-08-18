from odoo import models

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _check_expiration_date(self):
        """
        Algunos flujos hacen la comprobación por línea de movimiento.
        Cortocircuitamos aquí también para evitar avisos.
        """
        return True