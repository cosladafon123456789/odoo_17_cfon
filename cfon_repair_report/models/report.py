
from odoo import models, fields, api

class RepairReport(models.Model):
    _name = "repair.report"
    _description = "Informe diario de reparaciones"
    _order = "date desc, id desc"

    technician_id = fields.Many2one("res.users", string="Técnico", required=True, index=True)
    repair_id = fields.Many2one("repair.order", string="Orden de reparación", required=True, ondelete="cascade")
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
    ], string="Motivo", required=True, index=True)
    date = fields.Datetime(string="Fecha", default=fields.Datetime.now, required=True, index=True)

    @api.model
    def create_report(self, repair, reason):
        return self.create({
            "technician_id": self.env.user.id,
            "repair_id": repair.id,
            "reason": reason,
            "date": fields.Datetime.now(),
        })
