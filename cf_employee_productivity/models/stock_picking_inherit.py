from odoo import api, fields, models
from .res_config_settings import PARAM_PICKING_USERS

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super().button_validate()
        # Log only if current user is configured
        user = self.env.user
        configured_ids = self.env["res.config.settings"]._get_configured_user_ids(PARAM_PICKING_USERS)
        if user and user.id in configured_ids:
            for picking in self:
                self.env["employee.productivity.log"].sudo().create({
                    "user_id": user.id,
                    "action_type": "picking",
                    "related_model": "stock.picking",
                    "related_id": picking.id,
                })
        return res
