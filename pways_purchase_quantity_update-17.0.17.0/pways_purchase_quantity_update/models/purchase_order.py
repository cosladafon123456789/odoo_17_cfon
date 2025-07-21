from odoo import api, exceptions, fields, models, _

class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_qty = fields.Float(string='Quantity', compute="_compute_product_qty")
    purchase_id = fields.Many2one('purchase.order')
    state = fields.Selection([('hide', 'Hide'), ('show', 'Show')], default='hide', compute="_compute_state")

    def _compute_state(self):
        self.state = self._context.get('state')
        self.purchase_id = self.env["purchase.order"].browse(self._context.get('purchase_id'))

    def _compute_product_qty(self):
        for product_id in self:
            product_id.product_qty = self.env['purchase.order.line'].search([('order_id', '=', self.purchase_id.id), ('product_id', '=', product_id.id)]).product_qty

    def plus_qty(self):
        if self.product_qty == 0:
            self.env['purchase.order.line'].create({
                            'order_id': self.purchase_id.id,
                            'product_id': self.id,
                            'name': self.name, 
                            'product_qty': self.product_qty, 
                            'price_unit': self.list_price, 
                            })
        order_ids = self.env['purchase.order.line'].search([('order_id', '=', self.purchase_id.id), ('product_id', '=', self.id)])
        order_ids.product_qty += 1
        return True

    def minus_qty(self):
        if self.product_qty == 1:
            self.env['purchase.order.line'].search([('order_id', '=', self.purchase_id.id),('product_id', '=', self.id)]).unlink()
        order_ids = self.env['purchase.order.line'].search([('order_id', '=', self.purchase_id.id),('product_id', '=', self.id)])
        order_ids.product_qty -= 1
        return True

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order'

    def action_product_qty(self):
        view_id = self.env.ref('product.product_kanban_view').id
        return{
            'type': 'ir.actions.act_window',
            'name': "Products",
            'res_model': 'product.product',
            'view_mode': 'kanban',
            'view' : [[view_id, 'kanban']],
            'context': {'purchase_id': self.id, 'state': 'show'},
        }
        