from odoo import models

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _domain_location_id(self):
        # Permitir mostrar también ubicaciones de proveedor
        return [('usage', 'in', ['internal', 'supplier'])]
