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
        ("camara", "Sustitución de cámara"),
        ("carga", "Cambio de conector de carga"),
        ("placa", "Reparación de placa base"),
        ("limpieza", "Limpieza interna"),
        ("diagnostico", "Diagnóstico sin reparación"),
        ("bateria_nueva", "Batería nueva (instalada recientemente)"),
        ("bateria_100", "Batería 100 % de salud"),
        ("otro", "Otro motivo personalizado"),
    ], string="Motivo", required=True)
    notes = fields.Char("Detalle (opcional)")

    def action_confirm(self):
        self.ensure_one()
        company_user = self.env.company.cf_user_repair_id or self.env.user
        self.env["cf.productivity.line"].sudo().log_entry(
            user=company_user,
            type_key="repair",
            reason=dict(self._fields["reason"].selection).get(self.reason),
            ref_model="repair.order",
            ref_id=self.repair_id.id,
        )
        # Continuar flujo estándar (marcar como hecho)
        return self.repair_id.with_context(reason_from_wizard=True).action_repair_done()
