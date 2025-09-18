from odoo import models, fields, api
import re

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    sale_order_id = fields.Many2one('sale.order', string='Pedido de Venta')

    @api.model_create_multi
    def create(self, vals_list):
        tickets = super().create(vals_list)
        for ticket in tickets:
            ticket._auto_link_sale_order()
        return tickets

    def write(self, vals):
        res = super().write(vals)
        if 'name' in vals:
            for ticket in self:
                ticket._auto_link_sale_order()
        return res

    def _auto_link_sale_order(self):
        if self.name:
            match = re.search(r'(SO\d+)', self.name)
            if match:
                order_name = match.group(1)
                order = self.env['sale.order'].search([('name', '=', order_name)], limit=1)
                if order:
                    self.sale_order_id = order
