# -*- coding: utf-8 -*-
from odoo import api, fields, models

class RepairReasonWizard(models.TransientModel):
    _name = "repair.reason.wizard"
    _description = "Asistente de motivo de reparación"

    repair_id = fields.Many2one("repair.order", string="Reparación", required=True)
    reason = fields.Selection([
        ("pantalla", "Cambio de pantalla"),
        ("bateria", "Cambio de batería"),
        ("bateria_usada", "Cambio de batería usada"),
        ("bateria_nueva_100", "Batería nueva 100%"),
        ("camara", "Sustitución de cámara"),
        ("carga", "Cambio de conector de carga"),
        ("placa", "Reparación de placa base"),
        ("limpieza", "Limpieza interna"),
        ("otros", "Otros"),
    ], string="Motivo", required=True)
    notes = fields.Char("Detalle (opcional)")

    def action_confirm(self):
        self.ensure_one()
        company_user = self.env.company.cf_user_repair_id or self.env.user
        reason_label = dict(self._fields["reason"].selection).get(self.reason)
        note = reason_label if not self.notes else f"{reason_label} - {self.notes}"
        self.env["cf.productivity.line"].sudo().log_entry(
            user=company_user,
            type_key="repair",
            reason=note,
            ref_model="repair.order",
            ref_id=self.repair_id.id,
        )
        return self.repair_id.with_context(reason_from_wizard=True).action_repair_done()
