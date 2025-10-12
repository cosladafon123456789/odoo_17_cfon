# -*- coding: utf-8 -*-
from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    cf_user_repair_id = fields.Many2one(
        "res.users",
        string="Usuario de reparaciones",
        help="Usuario que se contabilizará al finalizar una reparación."
    )
    cf_user_ticket_id = fields.Many2one(
        "res.users",
        string="Usuario de tickets",
        help="Usuario que se contabilizará al responder un ticket."
    )
    cf_user_order_id = fields.Many2one(
        "res.users",
        string="Usuario de pedidos/entregas",
        help="Usuario que se contabilizará al validar una entrega de venta."
    )