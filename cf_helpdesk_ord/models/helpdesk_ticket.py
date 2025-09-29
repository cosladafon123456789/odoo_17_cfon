from odoo import models, fields

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    linked_sale_order_id = fields.Many2one(
        "sale.order", string="Pedido relacionado"
    )
