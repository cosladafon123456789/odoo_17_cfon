from odoo import models

class StockLot(models.Model):
    _inherit = 'stock.lot'

    def print_imei_label(self):
        return self.env.ref('serial_imei_label.report_serial_label').report_action(self)
