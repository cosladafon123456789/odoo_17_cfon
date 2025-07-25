from odoo import models, fields, api
import re

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    linked_sale_order_id = fields.Many2one('sale.order', string='Pedido relacionado', compute='_compute_linked_sale_order', store=True)

    @api.depends('name')
    def _compute_linked_sale_order(self):
        pattern = r'(SO\\d+)'  # Ajusta esto al formato real de tus pedidos
        for ticket in self:
            ticket.linked_sale_order_id = False
            match = re.search(pattern, ticket.name or '')
            if match:
                order = self.env['sale.order'].search([('name', '=', match.group(1))], limit=1)
                if order:
                    ticket.linked_sale_order_id = order.id
