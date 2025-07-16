from odoo import models

class StockLot(models.Model):
    _inherit = 'stock.lot'

    def print_serial_label(self):
        return self.env.ref('serial_label_standard_v2.report_serial_label').report_action(self)
