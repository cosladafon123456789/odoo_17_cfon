from odoo import fields, models, api, _
from datetime import date
from odoo.exceptions import ValidationError

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    parent_analytic_id = fields.Many2one('account.analytic.account', string="Parent Analytic Account")