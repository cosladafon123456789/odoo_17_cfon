# -*- coding: utf-8 -*-

from odoo import fields, models


class IrActionsPrintOptions(models.Model):
    _inherit = 'ir.actions.report'

    print_options = fields.Selection(selection=[
        ('print', 'Print'),
        ('save', 'Save'),
        ('view', 'View')
    ], string='Printing Options')

    def _get_readable_fields(self):
        datas = super()._get_readable_fields()
        datas.add('print_options')
        return datas

    def report_action(self, doc_ids, datas=None, config=True):
        datas = super(IrActionsPrintOptions, self).report_action(doc_ids, datas, config)
        datas['id'] = self.id
        datas['print_options'] = self.print_options
        return datas
