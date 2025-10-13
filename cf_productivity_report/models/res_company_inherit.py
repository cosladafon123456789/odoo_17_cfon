# -*- coding: utf-8 -*-
from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    cf_user_repair_id = fields.Many2one("res.users", string="Usuario de reparaciones")
    cf_user_ticket_id = fields.Many2one("res.users", string="Usuario de tickets")
    cf_user_order_id  = fields.Many2one("res.users", string="Usuario de pedidos/entregas")

# Timeout de reseteo en minutos para intervalos entre validaciones
cf_order_timeout_min = fields.Integer(
    string="Timeout validaciones (min)",
    default=30,
    help="Si entre validaciones pasa más de este tiempo, se considera nueva sesión y no se promedia."
)

