# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class CFProductivityRepairStats(models.Model):
    _name = "cf.productivity.repair.stats"
    _description = "Estadísticas de productividad (tiempo medio entre reparaciones finalizadas)"
    _auto = False
    _rec_name = "user_id"

    sort_key = fields.Integer(readonly=True)
    user_id = fields.Many2one("res.users", string="Usuario", readonly=True)
    avg_seconds = fields.Float(string="Segundos medios", readonly=True)
    avg_repair_interval = fields.Char(string="Tiempo medio entre reparaciones", compute="_compute_avg_text", readonly=True)

    _order = "sort_key, user_id, id"

    def _compute_avg_text(self):
        for rec in self:
            if not rec.user_id:
                rec.avg_repair_interval = (
                    "Definición de la métrica: "
                    "Se consideran todas las reparaciones registradas por usuario. "
                    "No se excluyen pausas ni intervalos prolongados. "
                    "El valor (HH:MM:SS) representa la media general del ritmo de cierre de reparaciones."
                )
                continue
            seconds = int(rec.avg_seconds or 0)
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            rec.avg_repair_interval = f"{h:02d}:{m:02d}:{s:02d}"

    def init(self):
        tools.drop_view_if_exists(self._cr, 'cf_productivity_repair_stats')
        self._cr.execute("""
            CREATE OR REPLACE VIEW cf_productivity_repair_stats AS
            WITH ordered AS (
                SELECT
                    user_id,
                    date,
                    date - LAG(date) OVER (PARTITION BY user_id ORDER BY date) AS delta
                FROM cf_productivity_line
                WHERE type = 'repair'
            ),
            agg AS (
                SELECT
                    user_id,
                    AVG(EXTRACT(EPOCH FROM delta)) AS avg_seconds
                FROM ordered
                WHERE delta IS NOT NULL
                GROUP BY user_id
            )
            SELECT
                user_id AS id,
                user_id,
                COALESCE(avg_seconds, 0) AS avg_seconds,
                0 AS sort_key
            FROM agg
            UNION ALL
            SELECT 2147483647 AS id, NULL::int4 AS user_id, NULL::float AS avg_seconds, 1 AS sort_key
        """)
