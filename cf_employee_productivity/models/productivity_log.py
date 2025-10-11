from odoo import api, fields, models, _
from collections import defaultdict

PARAM_SEND_DAILY = "cf_employee_productivity.send_daily_summary"
PARAM_RECIPIENT_IDS = "cf_employee_productivity.summary_recipient_ids"

class EmployeeProductivityLog(models.Model):
    _name = "employee.productivity.log"
    _description = "Employee Productivity Log"
    _order = "date desc, id desc"

    date = fields.Datetime(string="Fecha", default=lambda self: fields.Datetime.now(), index=True)
    user_id = fields.Many2one("res.users", string="Empleado", required=True, index=True)
    action_type = fields.Selection([
        ("picking", "Pedido"),
        ("repair", "Reparación"),
        ("ticket", "Ticket")
    ], string="Tipo de acción", required=True, index=True)

    related_model = fields.Char(string="Modelo relacionado")
    related_id = fields.Integer(string="ID relacionado")

    picking_id = fields.Many2one("stock.picking", string="Entrega", compute="_compute_relations", store=False)
    repair_id = fields.Many2one("repair.order", string="Reparación", compute="_compute_relations", store=False)
    ticket_id = fields.Many2one("helpdesk.ticket", string="Ticket", compute="_compute_relations", store=False)

    repair_reason_id = fields.Many2one("cf.repair.reason", string="Motivo de reparación")

    @api.depends("related_model", "related_id")
    def _compute_relations(self):
        for rec in self:
            rec.picking_id = False
            rec.repair_id = False
            rec.ticket_id = False
            if rec.related_model == "stock.picking" and rec.related_id:
                rec.picking_id = self.env["stock.picking"].browse(rec.related_id)
            elif rec.related_model == "repair.order" and rec.related_id:
                rec.repair_id = self.env["repair.order"].browse(rec.related_id)
            elif rec.related_model == "helpdesk.ticket" and rec.related_id:
                rec.ticket_id = self.env["helpdesk.ticket"].browse(rec.related_id)

    # ---------------- Daily summary email ----------------
    @api.model
    def _get_summary_recipients(self):
        icp = self.env["ir.config_parameter"].sudo()
        ids_param = icp.get_param(PARAM_RECIPIENT_IDS, default="")
        ids = [int(x) for x in ids_param.split(",") if x] if ids_param else []
        if not ids:
            admin = self.env.ref("base.user_admin", raise_if_not_found=False)
            return admin and admin.partner_id and [admin.partner_id] or []
        partners = self.env["res.users"].sudo().browse(ids).mapped("partner_id")
        return [p for p in partners if p.email]

    @api.model
    def _is_daily_summary_enabled(self):
        icp = self.env["ir.config_parameter"].sudo()
        return icp.get_param(PARAM_SEND_DAILY, default="1") in ("1", "True", "true")

    @api.model
    def _today_range(self):
        today = fields.Date.context_today(self)
        start_dt = fields.Datetime.to_datetime(f"{today} 00:00:00")
        end_dt = fields.Datetime.to_datetime(f"{today} 23:59:59")
        return start_dt, end_dt

    @api.model
    def _compute_daily_stats(self, date_from=None, date_to=None):
        if not date_from or not date_to:
            date_from, date_to = self._today_range()
        domain = [("date", ">=", date_from), ("date", "<=", date_to)]
        logs = self.search(domain)
        per_user = defaultdict(lambda: {"picking": 0, "repair": 0, "ticket": 0, "total": 0})
        for l in logs:
            per_user[l.user_id.name][l.action_type] += 1
            per_user[l.user_id.name]["total"] += 1
        totals = {"picking": 0, "repair": 0, "ticket": 0, "total": len(logs)}
        for v in per_user.values():
            totals["picking"] += v["picking"]
            totals["repair"] += v["repair"]
            totals["ticket"] += v["ticket"]
        ranking = sorted(per_user.items(), key=lambda kv: kv[1]["total"], reverse=True)
        return per_user, totals, ranking

    @api.model
    def _render_html_summary(self, date_from=None, date_to=None):
        per_user, totals, ranking = self._compute_daily_stats(date_from, date_to)
        rows = []
        for name, data in ranking:
            rows.append("<tr><td>{}</td><td style='text-align:center'>{}</td><td style='text-align:center'>{}</td><td style='text-align:center'>{}</td><td style='text-align:center'><b>{}</b></td></tr>".format(
                name, data['picking'], data['repair'], data['ticket'], data['total']
            ))
        if not rows:
            rows.append("<tr><td colspan='5' style='text-align:center;color:#888'>No hay actividad registrada hoy.</td></tr>")
        table = (
        "<table style='border-collapse:collapse;width:100%'>"
        "<thead>"
        "<tr>"
        "<th style='border-bottom:1px solid #ddd;text-align:left;padding:6px'>Empleado</th>"
        "<th style='border-bottom:1px solid #ddd;text-align:center;padding:6px'>Pedidos</th>"
        "<th style='border-bottom:1px solid #ddd;text-align:center;padding:6px'>Reparaciones</th>"
        "<th style='border-bottom:1px solid #ddd;text-align:center;padding:6px'>Tickets</th>"
        "<th style='border-bottom:1px solid #ddd;text-align:center;padding:6px'>Total</th>"
        "</tr>"
        "</thead>"
        "<tbody>{rows}</tbody>"
        "</table>"
        "<p style='margin-top:12px'><b>Totales globales:</b> Pedidos {p} — Reparaciones {r} — Tickets {t}</p>"
        ).format(rows="".join(rows), p=totals['picking'], r=totals['repair'], t=totals['ticket'])
        return table

    @api.model
    def cron_send_daily_summary(self):
        if not self._is_daily_summary_enabled():
            return
        recipients = self._get_summary_recipients()
        if not recipients:
            return
        date_from, date_to = self._today_range()
        html = self._render_html_summary(date_from, date_to)
        subject = _("📊 Resumen de productividad — %s") % fields.Date.to_string(fields.Date.context_today(self))
        email_to = ",".join([p.email for p in recipients if p.email])
        if not email_to:
            return
        mail_vals = {
            "subject": subject,
            "email_to": email_to,
            "body_html": "<div>{}</div>".format(html),
            "auto_delete": True,
        }
        self.env["mail.mail"].sudo().create(mail_vals).send()
