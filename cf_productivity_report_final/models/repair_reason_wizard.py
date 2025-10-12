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
        # Solo garantiza que el wizard existe; la lógica de finalización se implementa en el heredado de repair.order
        return {"type": "ir.actions.act_window_close"}
