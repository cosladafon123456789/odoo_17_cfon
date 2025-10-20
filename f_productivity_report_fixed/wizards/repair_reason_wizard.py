# -*- coding: utf-8 -*-
from odoo import fields, models

class RepairReasonWizard(models.TransientModel):
    _name = "repair.reason.wizard"
    _description = "Asistente de motivo de reparación"

    repair_id = fields.Many2one("repair.order", string="Reparación", required=True)
    reason = fields.Selection([
        ("pantalla", "Cambio de pantalla"),
        ("bateria", "Cambio de batería (nueva)"),
        ("bateria_usada", "Cambio de batería (usada)"),
        ("bateria_100", "Batería nueva 100%"),
        ("camara", "Sustitución de cámara"),
        ("carga", "Cambio de conector de carga"),
        ("placa", "Reparación de placa base"),
        ("limpieza", "Limpieza interna"),
        ("otros", "Otros"),
    ], string="Motivo", required=True)
    notes = fields.Char("Detalle (opcional)")

    def action_confirm(self):
        self.ensure_one()
        label = dict(self._fields["reason"].selection).get(self.reason)
        if self.notes:
            label = f"{label} - {self.notes}"
        # Registrar productividad para el usuario que confirma
        self.env["cf.productivity.line"].sudo().log_entry(
            user=self.env.user,
            type_key="repair",
            reason=label,
            ref_model="repair.order",
            ref_id=self.repair_id.id,
        )
        # Continuar con el flujo normal marcando como hecho
        return self.repair_id.with_context(reason_from_wizard=True).action_repair_done()
