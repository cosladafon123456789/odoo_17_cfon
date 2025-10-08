# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    marketplace_account_ids = fields.One2many(
        related="company_id.marketplace_account_ids",
        readonly=False
    )

class ResCompany(models.Model):
    _inherit = "res.company"

    marketplace_account_ids = fields.One2many("marketplace.account","company_id")
