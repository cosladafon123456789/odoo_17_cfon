# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    cf_user_repair_id = fields.Many2one("res.users", string="Usuario para Reparaciones")
    cf_user_ticket_id = fields.Many2one("res.users", string="Usuario para Tickets")
    cf_user_order_id  = fields.Many2one("res.users", string="Usuario para Pedidos/Entregas")
