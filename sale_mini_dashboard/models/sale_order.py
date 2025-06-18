from odoo import api, models
from odoo.tools import format_amount


class SaleOrder(models.Model):
    """Inherited the model for adding the dashboard values"""
    _inherit = 'sale.order'

    @api.model
    def get_dashboard_values(self):
        """This method returns values to the dashboard in sale order views."""
        result = {
            'total_orders': 0,
            'draft_orders': 0,
            'sale_orders': 0,
            'my_orders': 0,
            'my_draft_orders': 0,
            'my_sale_orders': 0,
            'total_sale_amount': 0,
            'total_draft_amount': 0,
        }
        sale_order = self.env['sale.order']
        user = self.env.user
        result['total_orders'] = sale_order.search_count([])
        result['draft_orders'] = sale_order.search_count(
            [('state', 'in', ['draft', 'sent'])])
        result['sale_orders'] = sale_order.search_count(
            [('state', 'in', ['sale', 'done'])])
        result['my_orders'] = sale_order.search_count(
            [('user_id', '=', user.id)])
        result['my_draft_orders'] = sale_order.search_count(
            [('user_id', '=', user.id), ('state', 'in', ['draft', 'sent'])])
        result['my_sale_orders'] = sale_order.search_count(
            [('user_id', '=', user.id), ('state', 'in', ['sale', 'done'])])
        order_sum = """select sum(amount_total) from sale_order where state 
        in ('sale', 'done')"""
        self._cr.execute(order_sum)
        res = self.env.cr.fetchone()
        result['total_sale_amount'] = format_amount(self.env, res[0] or 0,
                                                    self.env.company.currency_id)
        draft_sum = """select sum(amount_total) from sale_order where state 
        in ('draft', 'sent')"""
        self._cr.execute(draft_sum)
        res = self.env.cr.fetchone()
        result['total_draft_amount'] = format_amount(self.env, res[0] or 0,
                                                     self.env.company.currency_id)
        return result

    @api.model
    def get_dashboard_values_so(self):
        """This method returns values to the dashboard in sale order views."""
        result = {
            'total_orders': 0,
            'my_orders': 0,
            'pending_inv': 0,
            'my_pending_inv': 0,
            'pending_picking': 0,
            'my_pending_picking': 0,
        }
        sale_order = self.env['sale.order']
        user = self.env.user
        result['total_orders'] = sale_order.search_count([('state', 'not in', ('draft', 'sent', 'cancel'))])
        result['my_orders'] = sale_order.search_count([('user_id', '=', user.id), ('state', 'not in', ('draft', 'sent', 'cancel'))])
        result['pending_inv'] = sale_order.search_count([('state', 'not in', ('draft', 'sent', 'cancel')), ('invoice_status', '!=', 'invoiced')])
        result['my_pending_inv'] = sale_order.search_count([('user_id', '=', user.id), ('state', 'not in', ('draft', 'sent', 'cancel')), ('invoice_status', '!=', 'invoiced')])
        result['pending_picking'] = sale_order.search_count([('state', 'not in', ('draft', 'sent', 'cancel')), ('delivery_status', '!=', 'full')])
        result['my_pending_picking'] = sale_order.search_count([('user_id', '=', user.id), ('state', 'not in', ('draft', 'sent', 'cancel')), ('delivery_status', '!=', 'full')])

        order_sum = """select sum(amount_total) from sale_order where state in ('sale')"""
        self._cr.execute(order_sum)
        res = self.env.cr.fetchone()
        result['total_sale_amount'] = format_amount(self.env, res[0] or 0, self.env.company.currency_id)

        my_order_sum = """SELECT SUM(amount_total) FROM sale_order WHERE state = 'sale' AND user_id = %s"""
        self._cr.execute(my_order_sum, (user.id,))        
        res = self.env.cr.fetchone()
        result['my_sale_amount'] = format_amount(self.env, res[0] or 0, self.env.company.currency_id)
        return result
