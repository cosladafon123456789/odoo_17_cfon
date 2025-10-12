# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime, timedelta

class CFProductivityGoal(models.Model):
    _name = "cf.productivity.goal"
    _description = "Objetivos de productividad por usuario"
    _order = "user_id, period_start desc"

    user_id = fields.Many2one("res.users", string="Usuario", required=True, index=True)
    period_type = fields.Selection([("day","Día"),("week","Semana"),("month","Mes"),("custom","Personalizado")], required=True, default="week")
    period_start = fields.Date("Inicio", required=True, default=lambda self: fields.Date.today())
    period_end = fields.Date("Fin", required=True)

    target_repair = fields.Integer("Objetivo Reparaciones", default=0)
    target_ticket = fields.Integer("Objetivo Tickets", default=0)
    target_order  = fields.Integer("Objetivo Pedidos", default=0)
    target_points = fields.Float("Objetivo Puntos", default=0.0)

    done_repair = fields.Integer("Hecho Reparaciones", compute="_compute_done", store=False)
    done_ticket = fields.Integer("Hecho Tickets", compute="_compute_done", store=False)
    done_order  = fields.Integer("Hecho Pedidos", compute="_compute_done", store=False)
    done_points = fields.Float("Puntos Acumulados", compute="_compute_done", store=False)
    progress_pct = fields.Float("Progreso (%)", compute="_compute_done", store=False)

    @api.onchange("period_type","period_start")
    def _onchange_period(self):
        if self.period_type == "day":
            self.period_end = self.period_start
        elif self.period_type == "week":
            start = fields.Date.from_string(self.period_start)
            self.period_end = fields.Date.to_string(start + timedelta(days=6))
        elif self.period_type == "month":
            start = fields.Date.from_string(self.period_start).replace(day=1)
            if start.month == 12:
                end = start.replace(year=start.year+1, month=1, day=1) - timedelta(days=1)
            else:
                end = start.replace(month=start.month+1, day=1) - timedelta(days=1)
            self.period_start = fields.Date.to_string(start)
            self.period_end = fields.Date.to_string(end)

    def _compute_done(self):
        Line = self.env["cf.productivity.line"].sudo()
        for g in self:
            dom = [
                ("user_id","=", g.user_id.id),
                ("date",">=", fields.Datetime.to_datetime(str(g.period_start) + " 00:00:00")),
                ("date","<=", fields.Datetime.to_datetime(str(g.period_end) + " 23:59:59")),
            ]
            lines = Line.search(dom)
            g.done_repair = sum(1 for l in lines if l.type=="repair")
            g.done_ticket = sum(1 for l in lines if l.type=="ticket")
            g.done_order  = sum(1 for l in lines if l.type=="order")
            g.done_points = sum(l.points for l in lines)
            target_sum = (g.target_points or 0.0) or float((g.target_repair or 0) * 2 + (g.target_order or 0) * 1.5 + (g.target_ticket or 0) * 1)
            g.progress_pct = 100.0 * (g.done_points or 0.0) / target_sum if target_sum else 0.0
