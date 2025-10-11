from odoo import models, fields, api

class ProductivityLog(models.Model):
    _name = "productivity.log"
    _description = "Registro de productividad de empleados"
    _order = "date desc"

    name = fields.Char(string="Descripción", required=True)
    user_id = fields.Many2one("res.users", string="Usuario", required=True, default=lambda self: self.env.user)
    date = fields.Datetime(string="Fecha", default=fields.Datetime.now, required=True)
    type = fields.Selection([
        ("picking", "Entrega (Stock Picking)"),
        ("repair", "Reparación (Repair Order)"),
        ("helpdesk", "Postventa (Helpdesk Ticket)"),
        ("other", "Otro")
    ], string="Tipo de actividad", required=True, default="other")
    duration = fields.Float(string="Duración (horas)", help="Tiempo invertido en la actividad")
    notes = fields.Text(string="Notas adicionales")

    day = fields.Date(string="Día", compute="_compute_day", store=True)
    week = fields.Char(string="Semana", compute="_compute_week", store=True)
    month = fields.Char(string="Mes", compute="_compute_month", store=True)

    @api.depends("date")
    def _compute_day(self):
        for rec in self:
            rec.day = rec.date.date() if rec.date else False

    @api.depends("date")
    def _compute_week(self):
        for rec in self:
            rec.week = rec.date.strftime("%Y-W%U") if rec.date else False

    @api.depends("date")
    def _compute_month(self):
        for rec in self:
            rec.month = rec.date.strftime("%Y-%m") if rec.date else False

    # Método llamado por el cron (dummy; envía resumen a los destinatarios si está activo)
    def cron_send_daily_summary(self):
        # En una implementación real, aquí se construiría el email y se enviaría
        # a los usuarios definidos en res.config.settings (summary_recipient_ids)
        # cuando send_daily_summary esté activo.
        return True
