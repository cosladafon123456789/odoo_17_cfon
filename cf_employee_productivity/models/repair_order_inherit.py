from odoo import api, fields, models, _
from odoo.exceptions import UserError
from .res_config_settings import PARAM_REPAIR_USERS

class CfRepairReason(models.Model):
    _name = "cf.repair.reason"
    _description = "Motivo de reparación"
    name = fields.Char(required=True)
    description = fields.Text()

class RepairOrder(models.Model):
    _inherit = "repair.order"

    repair_reason_id = fields.Many2one("cf.repair.reason", string="Motivo de reparación")

    def action_repair_done(self):
        # If user is configured and no reason yet, open wizard
        user = self.env.user
        configured_ids = self.env["res.config.settings"]._get_configured_user_ids(PARAM_REPAIR_USERS)
        for rec in self:
            if user and user.id in configured_ids and not rec.repair_reason_id:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "repair.reason.wizard",
                    "view_mode": "form",
                    "target": "new",
                    "context": {"active_id": rec.id},
                    "name": _("Motivo de reparación"),
                }
        # Otherwise proceed and log
        res = super().action_repair_done()
        for rec in self:
            if user and user.id in configured_ids:
                self.env["employee.productivity.log"].sudo().create({
                    "user_id": user.id,
                    "action_type": "repair",
                    "related_model": "repair.order",
                    "related_id": rec.id,
                    "repair_reason_id": rec.repair_reason_id.id or False,
                })
        return res

    def action_repair_done_with_reason(self):
        res = super().action_repair_done()
        user = self.env.user
        configured_ids = self.env["res.config.settings"]._get_configured_user_ids(PARAM_REPAIR_USERS)
        for rec in self:
            if user and user.id in configured_ids:
                self.env["employee.productivity.log"].sudo().create({
                    "user_id": user.id,
                    "action_type": "repair",
                    "related_model": "repair.order",
                    "related_id": rec.id,
                    "repair_reason_id": rec.repair_reason_id.id or False,
                })
        return res
