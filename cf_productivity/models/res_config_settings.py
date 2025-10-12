from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    picking_user_ids = fields.Many2many("res.users","cf_config_picking_user_rel","config_id","user_id",string="Usuarios de pedidos a contabilizar")
    repair_user_ids = fields.Many2many("res.users","cf_config_repair_user_rel","config_id","user_id",string="Usuarios técnicos a contabilizar")
    helpdesk_user_ids = fields.Many2many("res.users","cf_config_helpdesk_user_rel","config_id","user_id",string="Usuarios de postventa a contabilizar")
    send_daily_summary = fields.Boolean(string="Enviar resumen diario por email", default=True)
    summary_recipient_ids = fields.Many2many("res.users","cf_config_summary_user_rel","config_id","user_id",string="Destinatarios del resumen diario")

    @api.model
    def get_values(self):
        res = super().get_values()
        icp = self.env["ir.config_parameter"].sudo()

        def to_ids(s):
            return [int(x) for x in s.split(",") if x] if s else []

        res.update({
            "picking_user_ids": [(6,0,to_ids(icp.get_param("cf_productivity.picking_user_ids")))],
            "repair_user_ids": [(6,0,to_ids(icp.get_param("cf_productivity.repair_user_ids")))],
            "helpdesk_user_ids": [(6,0,to_ids(icp.get_param("cf_productivity.helpdesk_user_ids")))],
            "summary_recipient_ids": [(6,0,to_ids(icp.get_param("cf_productivity.summary_recipient_ids")))],
            "send_daily_summary": icp.get_param("cf_productivity.send_daily_summary","True") in ("True","1","true"),
        })
        return res

    def set_values(self):
        super().set_values()
        icp = self.env["ir.config_parameter"].sudo()

        def to_str(ids):
            return ",".join(map(str, ids)) if ids else ""

        icp.set_param("cf_productivity.picking_user_ids", to_str(self.picking_user_ids.ids))
        icp.set_param("cf_productivity.repair_user_ids", to_str(self.repair_user_ids.ids))
        icp.set_param("cf_productivity.helpdesk_user_ids", to_str(self.helpdesk_user_ids.ids))
        icp.set_param("cf_productivity.summary_recipient_ids", to_str(self.summary_recipient_ids.ids))
        icp.set_param("cf_productivity.send_daily_summary", "True" if self.send_daily_summary else "False")
