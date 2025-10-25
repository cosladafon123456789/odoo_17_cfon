
# -*- coding: utf-8 -*-
from odoo import models, fields

class StockLot(models.Model):
    _inherit = 'stock.lot'

    # Campo booleano para marcar batería 100%
    x_bat100 = fields.Boolean(string='Batería 100%')
