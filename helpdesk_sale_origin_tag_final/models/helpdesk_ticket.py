from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    sale_origin_tag = fields.Char(string='Pedido de Origen', compute='_compute_sale_origin_tag')

    @api.depends('linked_sale_order_id.x_studio_origen')
    def _compute_sale_origin_tag(self):
        for ticket in self:
            origin = ticket.linked_sale_order_id.x_studio_origen
            ticket.sale_origin_tag = origin if origin else False

    @api.model_create_multi
    def create(self, vals_list):
        tickets = super().create(vals_list)
        tickets._assign_origin_tag()
        return tickets

    def write(self, vals):
        res = super().write(vals)
        self._assign_origin_tag()
        return res

    def _assign_origin_tag(self):
        for ticket in self:
            origin = ticket.linked_sale_order_id.x_studio_origen
            if origin:
                tag = self.env['helpdesk.tag'].search([('name', '=', origin)], limit=1)
                if not tag:
                    tag = self.env['helpdesk.tag'].create({'name': origin})
                if tag not in ticket.tag_ids:
                    ticket.tag_ids = [(4, tag.id)]
