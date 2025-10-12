# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class RepairReasonWizard(models.TransientModel):
    _name = "repair.reason.wizard"
    _description = "Motivo de Reparación"

    repair_id = fields.Many2one("repair.order", string="Reparación", required=True, ondelete="cascade")
    super_method = fields.Char()
    reason = fields.Selection([
        ("screen", "Cambio de pantalla"),
        ("battery_used", "Cambio de batería usada"),
        ("battery_new", "Batería nueva (instalada recientemente)"),
        ("battery_100", "Batería 100 % de salud"),
        ("camera", "Sustitución de cámara"),
        ("charge_port", "Cambio de conector de carga"),
        ("motherboard", "Reparación de placa base"),
        ("cleaning", "Limpieza interna"),
        ("no_fix", "Diagnóstico sin reparación"),
        ("other", "Otro motivo personalizado"),
    ], string="Motivo", required=True)
    reason_other = fields.Char("Detalle (si otro)")

    def action_confirm(self):
        self.ensure_one()
        reason_text = dict(self._fields["reason"].selection).get(self.reason)
        if self.reason == "other" and self.reason_other:
            reason_text = f"Otro: {self.reason_other}"
        # registrar productividad
        if self.env.company.cf_user_repair_id and self.env.company.cf_user_repair_id.id == self.env.user.id:
            self.env["cf.productivity.line"].sudo().log_entry(
                user=self.env.user,
                type_key="repair",
                reason=reason_text,
                ref_model="repair.order",
                ref_id=self.repair_id.id,
            )
        # llamar al método original para finalizar
        method = (self.super_method or "action_repair_done")
        return getattr(self.repair_id.with_context(cf_reason_captured=True), method)()