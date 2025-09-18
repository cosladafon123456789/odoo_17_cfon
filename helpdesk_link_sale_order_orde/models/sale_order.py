from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    helpdesk_ticket_ids = fields.One2many(
        'helpdesk.ticket',
        'sale_order_id',
        string='Tickets de Helpdesk Relacionados'
    )
