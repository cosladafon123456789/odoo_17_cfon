from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductHistory(models.TransientModel):
    _name = "product.history"
    _description = "Sale Add Product"
    
    purchase_history_ids = fields.One2many('purchase.history.lines', 'history_line_id', string="History", readonly=True)

    
    def default_get(self, vals):
        res = super(ProductHistory, self).default_get(vals)
        history_line_ids = [(5,0,0)]
        purchase_order_line_ids = self.env.context.get('active_id')
        purchase_line_id = self.env['purchase.order.line'].browse(purchase_order_line_ids)
        purchase_order_ids = self.env['purchase.order'].search([('order_line.product_id.id', '=', purchase_line_id.product_id.id)])
        for purchaseinfo in purchase_order_ids:
            for orderline in purchaseinfo.order_line:
                if orderline.product_id.id == purchase_line_id.product_id.id:
                    history_line_ids.append((0, 0, {'name': purchaseinfo.name, 'partner_id': purchaseinfo.partner_id.name, 'product_qty': orderline.product_qty, 'price_unit': orderline.price_unit}))
        res['purchase_history_ids'] = history_line_ids
        return res

class PurchaseHistoryLines(models.TransientModel):
    _name = "purchase.history.lines"

    check = fields.Boolean("check", default=False)
    history_line_id = fields.Many2one('product.history')
    name = fields.Char('Order')
    partner_id = fields.Char('Vendor')
    product_qty = fields.Float('Quantity')
    price_unit = fields.Float('Unit Price')
    