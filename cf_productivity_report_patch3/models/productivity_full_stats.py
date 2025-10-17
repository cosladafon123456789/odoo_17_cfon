# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class CFProductivityFullStats(models.Model):
    _name = "cf.productivity.full.stats"
    _description = "Resumen diario de productividad (volúmenes + tiempos medios por tipo)"
    _auto = False
    _rec_name = "user_id"
    _order = "date desc, user_id"

    user_id = fields.Many2one("res.users", string="Usuario", readonly=True)
    date = fields.Date(string="Fecha", readonly=True)

    count_orders = fields.Integer(string="Órdenes validadas", readonly=True)
    count_repairs = fields.Integer(string="Reparaciones finalizadas", readonly=True)
    count_tickets = fields.Integer(string="Tickets respondidos", readonly=True)

    avg_order_seconds = fields.Float(string="Segundos medios validación", readonly=True)
    avg_repair_seconds = fields.Float(string="Segundos medios reparación", readonly=True)
    avg_ticket_seconds = fields.Float(string="Segundos medios ticket", readonly=True)

    avg_order_text = fields.Char(string="⏱ Medio validación", compute="_compute_texts", readonly=True)
    avg_repair_text = fields.Char(string="⏱ Medio reparación", compute="_compute_texts", readonly=True)
    avg_ticket_text = fields.Char(string="⏱ Medio ticket", compute="_compute_texts", readonly=True)

    def _fmt(self, seconds):
        seconds = int(seconds or 0)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _compute_texts(self):
        for rec in self:
            rec.avg_order_text = self._fmt(rec.avg_order_seconds)
            rec.avg_repair_text = self._fmt(rec.avg_repair_seconds)
            rec.avg_ticket_text = self._fmt(rec.avg_ticket_seconds)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'cf_productivity_full_stats')
        self._cr.execute("""
            CREATE OR REPLACE VIEW cf_productivity_full_stats AS
            WITH base AS (
                SELECT
                    user_id,
                    DATE(date) AS d,
                    type,
                    date,
                    date - LAG(date) OVER (PARTITION BY user_id, type ORDER BY date) AS delta
                FROM cf_productivity_line
            ),
            agg AS (
                SELECT
                    user_id,
                    d AS date,
                    COUNT(*) FILTER (WHERE type = 'order')  AS count_orders,
                    COUNT(*) FILTER (WHERE type = 'repair') AS count_repairs,
                    COUNT(*) FILTER (WHERE type = 'ticket') AS count_tickets,
                    AVG(EXTRACT(EPOCH FROM delta)) FILTER (WHERE type = 'order')  AS avg_order_seconds,
                    AVG(EXTRACT(EPOCH FROM delta)) FILTER (WHERE type = 'repair') AS avg_repair_seconds,
                    AVG(EXTRACT(EPOCH FROM delta)) FILTER (WHERE type = 'ticket') AS avg_ticket_seconds
                FROM base
                GROUP BY user_id, d
            )
            SELECT
                ROW_NUMBER() OVER (ORDER BY date DESC, user_id) AS id,
                user_id,
                date,
                COALESCE(count_orders, 0)       AS count_orders,
                COALESCE(avg_order_seconds, 0)  AS avg_order_seconds,
                COALESCE(count_repairs, 0)      AS count_repairs,
                COALESCE(avg_repair_seconds, 0) AS avg_repair_seconds,
                COALESCE(count_tickets, 0)      AS count_tickets,
                COALESCE(avg_ticket_seconds, 0) AS avg_ticket_seconds
            FROM agg
        """)
