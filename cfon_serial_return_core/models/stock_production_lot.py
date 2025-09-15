
# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    return_count = fields.Integer(
        string="Return count",
        help="Times this serial/lot has been returned from a Customer to Internal stock.",
        default=0,
        readonly=True,
    )
