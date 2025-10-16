# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from datetime import timedelta

class CFProductivityStats(models.Model):
    _name = "cf.productivity.stats"
    _description = "Estadísticas de productividad (tiempo medio entre validaciones)"
    _auto = False
    _rec_name = "user_id"
    _order = "user_id,id"

    user_id = fields.Many2one("res.users", string="Usuario", readonly=True)
    avg_seconds = fields.Float(string="Segundos medios", readonly=True)
    avg_order_interval = fields.Char(string="Tiempo medio entre validaciones", compute="_compute_avg_text")

    def _compute_avg_text(self):
    for rec in self:
        # If synthetic footer row (no user), display explanatory rules instead of a time
        if not rec.user_id:
            rec.avg_order_interval = ("Definición de la métrica: "
                                      "Se consideran solo las 15 validaciones más recientes por usuario. "
                                      "Se excluyen intervalos superiores a 30 minutos para evitar que pausas o incidencias distorsionen la métrica. "
                                      "El valor (HH:MM:SS) refleja el ritmo durante actividad continua.")
            continue
        seconds = int(rec.avg_seconds or 0)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        rec.avg_order_interval = f"{h:02d}:{m:02d}:{s:02d}"

    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'cf_productivity_stats')
        self._cr.execute("""
            CREATE OR REPLACE VIEW cf_productivity_stats AS
            WITH ranked AS (
                SELECT
                    user_id,
                    date,
                    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY date DESC) AS rn
                FROM cf_productivity_line
                WHERE type = 'order'
            ),
            limited AS (
                SELECT user_id, date
                FROM ranked
                WHERE rn <= 15
            ),
            ordered AS (
                SELECT
                    user_id,
                    date,
                    date - LAG(date) OVER (PARTITION BY user_id ORDER BY date) AS delta
                FROM limited
            ),
            agg AS (
                SELECT
                    user_id,
                    AVG(EXTRACT(EPOCH FROM delta)) AS avg_seconds
                FROM ordered
                WHERE delta IS NOT NULL
                  AND EXTRACT(EPOCH FROM delta) <= 1800  -- excluir pausas > 30 min
                GROUP BY user_id
            )
            SELECT
                user_id AS id,
                user_id,
                COALESCE(avg_seconds, 0) AS avg_seconds
            FROM agg
        """)
