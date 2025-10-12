# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class RepairOrder(models.Model):
    _inherit = "repair.order"

    responsible_id = fields.Many2one("res.users", string="Responsable", tracking=True)

    def _cf_should_count_repair(self):
        # Count only if current user matches configured user for repairs
        company = self.env.company
        return company.cf_user_repair_id and company.cf_user_repair_id.id == self.env.user.id

    def action_repair_done(self):
        # Hook common method name
        action = self._cf_open_reason_wizard_if_needed(super_method="action_repair_done")
        return action

    def action_repair_end(self):
        # Some databases use this method name; keep compatibility
        action = self._cf_open_reason_wizard_if_needed(super_method="action_repair_end")
        return action

    def _cf_open_reason_wizard_if_needed(self, super_method):
        self.ensure_one()
        if self._cf_should_count_repair() and not self.env.context.get("cf_reason_captured"):
            # Open wizard to capture reason
            return {
                "name": _("Motivo de reparación"),
                "type": "ir.actions.act_window",
                "res_model": "repair.reason.wizard",
                "view_mode": "form",
                "target": "new",
                "context": {
                    "default_repair_id": self.id,
                    "default_super_method": super_method,
                },
            }
        # If not counting (or already captured), just call the original
        return getattr(super(RepairOrder, self), super_method)()