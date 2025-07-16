from odoo import models

class StockLot(models.Model):
    _inherit = 'stock.lot'

    def print_serial_label(self):
        return self.env.ref('serial_label_test_v6.report_serial_test').report_action(self)
