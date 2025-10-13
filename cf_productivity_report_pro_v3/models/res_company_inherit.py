
# -*- coding: utf-8 -*-
from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    cf_user_repair_id = fields.Many2one("res.users", string="Usuario de reparaciones")
    cf_user_ticket_id = fields.Many2one("res.users", string="Usuario de tickets")
    cf_user_order_id  = fields.Many2one("res.users", string="Usuario de pedidos/entregas")
    cf_inactivity_minutes = fields.Integer("Inactividad para bloques (min)", default=30,
        help="Si entre dos acciones pasan más de estos minutos, se considera un nuevo bloque de trabajo para el cálculo de tiempo efectivo.")
    cf_order_reset_minutes = fields.Integer("Reseteo entre pedidos (min)", default=30,
        help="Al calcular la media entre pedidos, si pasan más de estos minutos entre validaciones se considera un nuevo bloque (no cuenta como intervalo).")
