# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    lot_id = fields.Many2one(
        'stock.lot',
        string="Lot/Serial Number",
        compute="_compute_lot_id",
        search="_search_lot_id",
    )

    def _compute_lot_id(self):
        for product in self:
            lot = self.env['stock.lot'].search([('product_id', '=', product.id)], limit=1)
            product.lot_id = lot

    def _search_lot_id(self, operator, value):
        lots = self.env['stock.lot'].search([('name', operator, value)])
        return [('id', 'in', lots.mapped('product_id').ids)]
