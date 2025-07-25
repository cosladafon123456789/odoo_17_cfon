from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    sale_origin_tag = fields.Char(string='Pedido de Origen', compute='_compute_sale_origin_tag')

    @api.depends('linked_sale_order_id.origin')
    def _compute_sale_origin_tag(self):
        for ticket in self:
            origin = ticket.linked_sale_order_id.origin
            ticket.sale_origin_tag = origin if origin else False
