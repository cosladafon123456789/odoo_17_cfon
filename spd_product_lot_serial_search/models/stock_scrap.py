# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    product_id = fields.Many2one(
        'product.product', 
        string="Product", 
        required=True,
        check_company=True,
        domain="[('type', 'in', ['product', 'consu'])]",
        context={'search_lot_id': True}
    )
