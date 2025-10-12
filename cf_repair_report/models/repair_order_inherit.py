
from odoo import models
from odoo.exceptions import UserError

class RepairOrder(models.Model):
    _inherit = "repair.order"

    def open_reason_wizard(self):
        self.ensure_one()
        if self.state not in ("under_repair", "confirmed"):
            raise UserError("Solo puedes finalizar reparaciones en estado 'Confirmado' o 'En reparación'.")
        return {
            "type": "ir.actions.act_window",
            "res_model": "repair.reason.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"active_id": self.id},
        }
