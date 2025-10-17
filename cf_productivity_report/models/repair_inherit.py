# -*- coding: utf-8 -*-
from odoo import api, fields, models

class RepairOrder(models.Model):
    _inherit = "repair.order"

    def action_repair_done(self):
        # Si viene del wizard, ejecutar flujo normal
        if self.env.context.get("reason_from_wizard"):
            return super().action_repair_done()

        # Abrir wizard de motivo antes de finalizar
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Motivo de reparación",
            "res_model": "repair.reason.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_repair_id": self.id,
            },
        }
