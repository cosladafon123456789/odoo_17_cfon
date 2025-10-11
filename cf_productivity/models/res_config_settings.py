from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    picking_user_ids = fields.Many2many(
        "res.users", string="Usuarios de pedidos a contabilizar"
    )
    repair_user_ids = fields.Many2many(
        "res.users", string="Usuarios técnicos a contabilizar"
    )
    helpdesk_user_ids = fields.Many2many(
        "res.users", string="Usuarios de postventa a contabilizar"
    )
    send_daily_summary = fields.Boolean(
        string="Enviar resumen diario por email", default=True
    )
    summary_recipient_ids = fields.Many2many(
        "res.users", string="Destinatarios del resumen diario"
    )

    # ---------------------------------------------------------------
    # Cargar valores desde ir.config_parameter
    # ---------------------------------------------------------------
    @api.model
    def get_values(self):
        res = super().get_values()
        icp = self.env["ir.config_parameter"].sudo()

        def str_to_ids(param):
            return [int(x) for x in param.split(",")] if param else []

        res.update({
            "picking_user_ids": [(6, 0, str_to_ids(icp.get_param("cf_productivity.picking_user_ids")))],
            "repair_user_ids": [(6, 0, str_to_ids(icp.get_param("cf_productivity.repair_user_ids")))],
            "helpdesk_user_ids": [(6, 0, str_to_ids(icp.get_param("cf_productivity.helpdesk_user_ids]()
