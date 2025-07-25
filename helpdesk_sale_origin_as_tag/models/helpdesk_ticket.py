from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    sale_origin_tag = fields.Char(string='Pedido de Origen', compute='_compute_sale_origin_tag')

    @api.depends('linked_sale_order_id.x_studio_origen')
    def _compute_sale_origin_tag(self):
        for ticket in self:
            origin = ticket.linked_sale_order_id.x_studio_origen
            ticket.sale_origin_tag = origin if origin else False

            # Asignar etiqueta automáticamente si hay origen
            if origin:
                tag = self.env['helpdesk.tag'].search([('name', '=', origin)], limit=1)
                if not tag:
                    tag = self.env['helpdesk.tag'].create({'name': origin})
                ticket.tag_ids = [(4, tag.id)]
