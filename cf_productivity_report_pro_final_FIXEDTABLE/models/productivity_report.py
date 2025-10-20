
from odoo import api, fields, models

class CFProductivityReport(models.Model):
    _name = "cf.productivity.report"
    _description = "CF Productivity Report"
    _order = "date_time asc"

    name = fields.Char(string="Descripción", required=True)
    user_id = fields.Many2one("res.users", string="Usuario", required=True, default=lambda self: self.env.user)
    date_time = fields.Datetime(string="Fecha/Hora", required=True, default=fields.Datetime.now)
    reason = fields.Char(string="Motivo")
    action_type = fields.Selection([("picking_validate", "Validación"), ("other", "Otro")], default="picking_validate")
    time_since_previous = fields.Char(string="Tiempo desde anterior", compute="_compute_time_since_previous")

    @api.depends("user_id", "date_time")
    def _compute_time_since_previous(self):
        for rec in self:
            delta_str = "00:00:00"
            if rec.user_id and rec.date_time:
                prev = self.search([("user_id", "=", rec.user_id.id), ("date_time", "<", rec.date_time)],
                                   order="date_time desc", limit=1)
                if prev:
                    delta = rec.date_time - prev.date_time
                    seconds = int(delta.total_seconds())
                    h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
                    delta_str = f"{h:02d}:{m:02d}:{s:02d}"
            rec.time_since_previous = delta_str
