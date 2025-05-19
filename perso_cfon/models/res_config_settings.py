# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

from odoo.addons.account.models.company import PEPPOL_LIST


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    #GAP V1
    rebu_journal_id = fields.Many2one(
        comodel_name="account.journal",
        related="company_id.rebu_journal_id",
        string=_("Journal"),
        readonly=False,
        check_company=True,
        domain="[('type', '=', 'general')]")