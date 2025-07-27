from odoo import models, fields, api

class HelpdeskTicketLinkedOrderLine(models.TransientModel):
    _name = 'helpdesk.ticket.linked.order.line'
    _description = 'Productos del pedido vinculado al ticket'

    ticket_id = fields.Many2one('helpdesk.ticket')
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

    def _compute_linked_order_lines(self):
        Line = self.env['helpdesk.ticket.linked.order.line']
        for ticket in self:
            Line.search([('ticket_id', '=', ticket.id)]).unlink()
            order = ticket.linked_sale_order_id
            if not order:
                continue
            for line in order.order_line:
                serials = line.move_ids.mapped('move_line_ids.lot_id.name')
                if not serials:
                    serials = ['']
                for serial in serials:
                    Line.create({
                        'ticket_id': ticket.id,
                        'order_name': order.name,
                        'date_order': order.date_order,
                        'product_id': line.product_id.id,
                        'serial_number': serial
                    })
