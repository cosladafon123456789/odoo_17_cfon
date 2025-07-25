from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    linked_sale_order_id = fields.Many2one('sale.order', string='Pedido relacionado', compute='_compute_linked_sale_order', store=True)

    @api.depends('name')
    def _compute_linked_sale_order(self):
        for ticket in self:
            ticket.linked_sale_order_id = False
            if ticket.name:
                order_code = ticket.name.split()[0].strip()
                order = self.env['sale.order'].search([('name', '=', order_code)], limit=1)
                if order:
                    ticket.linked_sale_order_id = order.id
