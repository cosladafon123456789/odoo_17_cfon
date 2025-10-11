from odoo import fields, models

class CfProductivitySettings(models.Model):
    _name = "cf.productivity.settings"
    _description = "Configuración de Productividad"
    _rec_name = "id"

    picking_user_ids = fields.Many2many("res.users", string="Usuarios de pedidos")
    repair_user_ids = fields.Many2many("res.users", string="Usuarios técnicos")
    helpdesk_user_ids = fields.Many2many("res.users", string="Usuarios postventa")
    send_daily_summary = fields.Boolean("Enviar resumen diario", default=True)
    summary_recipient_ids = fields.Many2many("res.users", string="Destinatarios resumen diario")
