from odoo import models, fields, api

class HelpdeskTicketLinkedOrderLine(models.Model):
    _name = 'helpdesk.ticket.linked.order.line'
    _description = 'Productos del pedido vinculado al ticket'

    ticket_id = fields.Many2one('helpdesk.ticket', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Producto')
    serial_number = fields.Char(string='Nº Serie')
    order_name = fields.Char(string='Pedido')
    date_order = fields.Datetime(string='Fecha de Compra')


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    linked_order_line_ids = fields.One2many(
        'helpdesk.ticket.linked.order.line', 'ticket_id',
        string='Productos del Pedido',
        compute='_compute_linked_order_lines',
        store=False
    )

    @api.depends('linked_sale_order_id')
    def _compute_linked_order_lines(self):
        Line = self.env['helpdesk.ticket.linked.order.line']
        for ticket in self:
            existing_lines = Line.search([('ticket_id', '=', ticket.id)])
            existing_lines.unlink()
            order = ticket.linked_sale_order_id
            created_ids = []
            if order:
                for line in order.order_line:
                    serials = line.move_ids.mapped('move_line_ids.lot_id.name') or ['']
                    for serial in serials:
                        new_line = Line.create({
                            'ticket_id': ticket.id,
                            'order_name': order.name,
                            'date_order': order.date_order,
                            'product_id': line.product_id.id,
                            'serial_number': serial
                        })
                        created_ids.append(new_line.id)
            ticket.linked_order_line_ids = [(6, 0, created_ids)]
