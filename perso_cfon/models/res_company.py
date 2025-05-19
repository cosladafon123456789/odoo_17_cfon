# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError, RedirectWarning

class ResCompany(models.Model):
    _inherit = 'res.company'

    #GAP V1
    rebu_journal_id = fields.Many2one("account.journal", string=_("REBU Journal for entries"))