from odoo import models

class StockLot(models.Model):
    _inherit = 'stock.lot'

    def print_serial_label(self):
        report = self.env['ir.actions.report']._get_report_from_name('serial_label_test_v7.report_serial_test_document')
        return report.report_action(self)
