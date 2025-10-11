from odoo import api, fields, models
import json

PARAM_PICKING_USERS = "cf_employee_productivity.picking_user_ids"
PARAM_REPAIR_USERS = "cf_employee_productivity.repair_user_ids"
PARAM_HELPDESK_USERS = "cf_employee_productivity.helpdesk_user_ids"

def _ids_to_param(ids):
    return ",".join(str(int(i)) for i in ids) if ids else ""

def _param_to_ids(param):
    if not param:
        return []
    try:
        return [int(x) for x in param.split(",") if x]
    except Exception:
        return []

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    picking_user_ids = fields.Many2many("res.users", string="Usuarios de pedidos a contabilizar",
                                        help="Usuarios cuyos pickings validados se contabilizan")
    repair_user_ids = fields.Many2many("res.users", string="Usuarios técnicos a contabilizar",
                                       help="Usuarios cuyas reparaciones finalizadas se contabilizan")
    helpdesk_user_ids = fields.Many2many("res.users", string="Usuarios de postventa a contabilizar",
                                         help="Usuarios cuyas respuestas en tickets se contabilizan")

    @api.model
    def get_values(self):
        res = super().get_values()
        icp = self.env["ir.config_parameter"].sudo()
        res.update(
            picking_user_ids=[(6, 0, _param_to_ids(icp.get_param(PARAM_PICKING_USERS)))],
            repair_user_ids=[(6, 0, _param_to_ids(icp.get_param(PARAM_REPAIR_USERS)))],
            helpdesk_user_ids=[(6, 0, _param_to_ids(icp.get_param(PARAM_HELPDESK_USERS)))],
        )
        return res

    def set_values(self):
        super().set_values()
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param(PARAM_PICKING_USERS, _ids_to_param(self.picking_user_ids.ids))
        icp.set_param(PARAM_REPAIR_USERS, _ids_to_param(self.repair_user_ids.ids))
        icp.set_param(PARAM_HELPDESK_USERS, _ids_to_param(self.helpdesk_user_ids.ids))

    # Helpers for other models
    @api.model
    def _get_configured_user_ids(self, param_key):
        icp = self.env["ir.config_parameter"].sudo()
        return _param_to_ids(icp.get_param(param_key))
