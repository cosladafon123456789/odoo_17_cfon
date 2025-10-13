# -*- coding: utf-8 -*-
from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    cf_user_repair_id = fields.Many2one("res.users", string="Usuario de reparaciones")
    cf_user_ticket_id = fields.Many2one("res.users", string="Usuario de tickets")
    cf_user_order_id  = fields.Many2one("res.users", string="Usuario de pedidos/entregas")

    productivity_reset_minutes = fields.Integer(
        string="Tiempo de reseteo (minutos)",
        default=120,
        help="Si el usuario pasa más de este tiempo sin validar pedidos, se reinicia el cómputo de intervalos entre validaciones."
    )
