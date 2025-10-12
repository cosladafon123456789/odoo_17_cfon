
from odoo import models, fields

class RepairReasonWizard(models.TransientModel):
    _name = "repair.reason.wizard"
    _description = "Motivo de la reparación"

    reason = fields.Selection([
        ('battery_change', 'Cambio de batería'),
        ('screen_change', 'Cambio de pantalla'),
        ('charging_port', 'Conector de carga'),
        ('microphone', 'Micrófono'),
        ('speaker', 'Altavoz'),
        ('camera', 'Cámara'),
        ('board_repair', 'Reparación de placa base'),
        ('software_update', 'Reinstalación / actualización software'),
        ('diagnostic_only', 'Solo diagnóstico'),
        ('other', 'Otro motivo'),
    ], string="Motivo de la reparación", required=True)

    def action_confirm(self):
        self.ensure_one()
        repair = self.env['repair.order'].browse(self.env.context.get('active_id'))
        self.env['repair.report'].create_report(repair, self.reason)
        repair.action_repair_end()
        return {"type": "ir.actions.act_window_close"}
