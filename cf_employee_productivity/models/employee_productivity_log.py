from odoo import models, fields, api
from datetime import datetime

class EmployeeProductivityLog(models.Model):
    _name = "employee.productivity.log"
    _description = "Registro de productividad de empleados"

    name = fields.Char(string="Descripción", compute="_compute_name", store=True)
    user_id = fields.Many2one("res.users", string="Empleado", required=True)
    task_type = fields.Selection([
        ("picking", "Pedido"),
        ("repair", "Reparación"),
        ("helpdesk", "Postventa"),
    ], string="Tipo de tarea", required=True)
    points = fields.Integer(string="Puntos", default=1)
    date = fields.Datetime(string="Fecha", default=fields.Datetime.now)

    @api.depends("user_id", "task_type", "date")
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.user_id.name} - {rec.task_type} - {rec.date.strftime('%Y-%m-%d %H:%M:%S')}"

    @api.model
    def cron_send_daily_summary(self):
        today = fields.Date.today()
        logs = self.search([("date", ">=", datetime.combine(today, datetime.min.time()))])
        summary = {}
        for log in logs:
            summary.setdefault(log.user_id.name, 0)
            summary[log.user_id.name] += log.points

        if summary:
            body = "<h3>Resumen diario de productividad</h3><ul>"
            for user, pts in summary.items():
                body += f"<li><b>{user}</b>: {pts} puntos</li>"
            body += "</ul>"
            admin_email = self.env.user.email or self.env.company.email
            if admin_email:
                self.env["mail.mail"].create({
                    "subject": "Resumen diario de productividad",
                    "body_html": body,
                    "email_to": admin_email
                }).send()
