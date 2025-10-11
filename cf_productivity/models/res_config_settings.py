from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    picking_user_ids = fields.Many2many("res.users", string="Usuarios de pedidos a contabilizar", config_parameter="cf_productivity.picking_user_ids")
    repair_user_ids = fields.Many2many("res.users", string="Usuarios técnicos a contabilizar", config_parameter="cf_productivity.repair_user_ids")
    helpdesk_user_ids = fields.Many2many("res.users", string="Usuarios de postventa a contabilizar", config_parameter="cf_productivity.helpdesk_user_ids")
    send_daily_summary = fields.Boolean("Enviar resumen diario por email", config_parameter="cf_productivity.send_daily_summary")
    summary_recipient_ids = fields.Many2many("res.users", string="Destinatarios del resumen diario", config_parameter="cf_productivity.summary_recipient_ids")
