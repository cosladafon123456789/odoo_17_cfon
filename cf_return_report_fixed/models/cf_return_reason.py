# -*- coding: utf-8 -*-
from odoo import models, fields

class CfReturnReason(models.Model):
    _name = "cf.return.reason"
    _description = "Motivo de devolución (CF)"

    name = fields.Char("Motivo", required=True)
    active = fields.Boolean(default=True)
