# -*- coding: utf-8 -*-
from odoo import models

class RepairOrder(models.Model):
    _inherit = "repair.order"

    def action_repair_done(self):
        self.ensure_one()
        # Abrir wizard si no viene del propio asistente
        if not self.env.context.get("reason_from_wizard"):
            return {
                "type": "ir.actions.act_window",
                "res_model": "repair.reason.wizard",
                "view_mode": "form",
                "target": "new",
                "context": {"default_repair_id": self.id},
            }
        return super().action_repair_done()
