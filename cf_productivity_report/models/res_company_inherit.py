# -*- coding: utf-8 -*-
from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    cf_user_repair_id = fields.Many2one("res.users", string="Usuario de reparaciones")
    cf_user_ticket_id = fields.Many2one("res.users", string="Usuario de tickets")
    cf_user_order_id  = fields.Many2one("res.users", string="Usuario de pedidos/entregas")
