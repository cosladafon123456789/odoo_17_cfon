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
        ("software", "Actualización de software"),
        ("diagnostico", "Diagnóstico sin reparación"),
        ("otro", "Otro motivo personalizado"),
    ], string="Motivo", required=True)
    super_method = fields.Char(string="Método a ejecutar")

    def action_confirm(self):
        if self.repair_id and self.super_method:
            method = getattr(self.repair_id, self.super_method, None)
            if method:
                return method()
        return True
