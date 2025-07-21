# -*- coding: utf-8 -*-
from odoo import api, models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    purchase_history_lines = fields.One2many('purchase.history.line', 'history_id', readonly=True)
    purchase_lines = fields.Many2one('purchase.order', compute="_compute_purchase_lines")

    def _compute_purchase_lines(self):
        for record in self:
            record.purchase_lines = []
            purchase_line_id = [(5,0,0)]
            purchase_order_ids = self.env['purchase.order'].search([('order_line.product_id.id', '=', record.id)])
            for purchaseinfo in purchase_order_ids:
                for orderline in purchaseinfo.order_line:
                    if orderline.product_id.id == record.id:
                        purchase_line_id.append((0, 0, {'name': purchaseinfo.name, 'partner_id': purchaseinfo.partner_id.name, 'product_qty': orderline.product_qty, 'price_unit': orderline.price_unit}))
            record.purchase_history_lines = purchase_line_id


class purchase_history_line(models.Model):
    _name = 'purchase.history.line'
    _description = 'purchase_history_line'

    history_id = fields.Many2one('product.product')
    name = fields.Char('Order')
    partner_id = fields.Char('Vendor')
    product_qty = fields.Float('Quantity')
    price_unit = fields.Float('Unit Price')

class SaleOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def purchase_history(self):
        view_id = self.env.ref('pways_purchase_history.product_history_wizard_view').id

        return {
            'type': 'ir.actions.act_window',
            'name': "history",
            'res_model': 'product.history',
            'target' : 'new',
            'view_mode': 'form',
            'view' : [[view_id, 'form']],
        }
