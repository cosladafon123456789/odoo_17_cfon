from odoo import fields, models, api, _

class HrExpenseInherit(models.Model):
    _inherit = 'hr.expense'

    paid_by = fields.Selection([
        ('employee', 'Employee'),
        ('company', 'Company')
    ])