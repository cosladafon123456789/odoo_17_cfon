from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    sale_origin_tag = fields.Char(string='Pedido de Origen', compute='_compute_sale_origin_tag', store=True)

    @api.depends('linked_sale_order_id')
    def _compute_sale_origin_tag(self):
        for ticket in self:
            if ticket.linked_sale_order_id and ticket.linked_sale_order_id.origin:
                ticket.sale_origin_tag = ticket.linked_sale_order_id.origin
            else:
                ticket.sale_origin_tag = False
