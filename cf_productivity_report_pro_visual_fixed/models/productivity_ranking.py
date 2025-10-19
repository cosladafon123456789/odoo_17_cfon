
from odoo import models, fields, api

class CfProductivityRanking(models.Model):
    _name = "cf.productivity.ranking"
    _description = "Ranking diario de productividad"
    _order = "day desc, score desc"

    day = fields.Date(string="Día", required=True, index=True, default=lambda self: fields.Date.context_today(self))
    user_id = fields.Many2one('res.users', string="Usuario", required=True, index=True)
    actions = fields.Integer(string="Acciones", default=0)
    avg_gap_hhmmss = fields.Char(string="Tiempo medio")
    pauses = fields.Integer(string="Pausas", default=0)
    score = fields.Float(string="Puntuación", help="Algoritmo simple: acciones - (pausas * 0.5)")

    @api.model
    def action_rebuild_today(self):
        day = fields.Date.context_today(self)
        self.search([('day', '=', day)]).unlink()
        Report = self.env['cf.productivity.report']
        start_dt = fields.Datetime.to_datetime(f"{day} 00:00:00")
        end_dt = fields.Datetime.to_datetime(f"{day} 23:59:59")
        users = self.env['res.users'].search([])
        for u in users:
            lines = Report.search([('user_id', '=', u.id), ('date', '>=', start_dt), ('date', '<=', end_dt)], order='date asc')
            if not lines:
                continue
            actions = len(lines)
            # compute pauses and avg
            prev = None
            gaps = []
            pauses = 0
            for l in lines:
                if prev:
                    gap = (l.date - prev.date).total_seconds()
                    gaps.append(gap)
                    if gap >= ((l.pause_threshold_min or 30) * 60):
                        pauses += 1
                prev = l
            avg = int(sum(gaps)/len(gaps)) if gaps else 0
            hh = avg // 3600
            mm = (avg % 3600) // 60
            ss = avg % 60
            avg_txt = f"{hh:02d}:{mm:02d}:{ss:02d}" if avg else ''
            score = actions - (pauses * 0.5)
            self.create({
                'day': day,
                'user_id': u.id,
                'actions': actions,
                'avg_gap_hhmmss': avg_txt,
                'pauses': pauses,
                'score': score,
            })
        return True
