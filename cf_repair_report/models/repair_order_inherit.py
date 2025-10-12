from odoo import models

class RepairOrder(models.Model):
    _inherit = "repair.order"

    def open_reason_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "repair.reason.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"active_id": self.id},
        }
