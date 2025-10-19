
from odoo import models, fields, api, tools

class CfProductivityStats(models.Model):
    _name = "cf.productivity.stats"
    _description = "Estadísticas de productividad (usuario/día)"
    _auto = False
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users', string="Usuario", readonly=True)
    day = fields.Date(string="Día", readonly=True)
    actions = fields.Integer(string="Acciones", readonly=True)
    avg_gap_sec = fields.Float(string="Promedio intervalo (s)", readonly=True)

    avg_gap_hhmmss = fields.Char(string="Tiempo medio", compute="_compute_hhmmss", store=False)

    def _compute_hhmmss(self):
        for rec in self:
            if not rec.avg_gap_sec:
                rec.avg_gap_hhmmss = ''
            else:
                total = int(rec.avg_gap_sec)
                hh = total // 3600
                mm = (total % 3600) // 60
                ss = total % 60
                rec.avg_gap_hhmmss = f"{hh:02d}:{mm:02d}:{ss:02d}"

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute('''
            CREATE or REPLACE VIEW %s AS (
                WITH ordered AS (
                    SELECT
                        id,
                        user_id,
                        date::date AS day,
                        date,
                        LAG(date) OVER (PARTITION BY user_id ORDER BY date) AS prev_date
                    FROM cf_productivity_report
                ),
                diffs AS (
                    SELECT
                        user_id,
                        day,
                        COUNT(*) AS actions,
                        AVG(EXTRACT(EPOCH FROM (date - prev_date))) AS avg_gap_sec
                    FROM ordered
                    WHERE prev_date IS NOT NULL
                    GROUP BY user_id, day
                )
                SELECT
                    ROW_NUMBER() OVER() as id,
                    user_id,
                    day,
                    actions,
                    COALESCE(avg_gap_sec, 0) as avg_gap_sec
                FROM diffs
            )
        ''' % self._table)
