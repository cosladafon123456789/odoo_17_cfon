
from odoo import api, fields, models
from datetime import datetime

class CFProductivityRanking(models.Model):
    _name = "cf.productivity.ranking"
    _description = "Ranking Productividad"
    _order = "ranking_date desc, score desc"

    user_id = fields.Many2one("res.users", string="Usuario", required=True)
    ranking_date = fields.Date(string="Fecha", required=True, default=fields.Date.context_today)
    score = fields.Integer(string="Puntuación", default=0)
    lines_count = fields.Integer(string="# Validaciones", default=0)

    def action_rebuild_today(self):
        today = fields.Date.context_today(self)
        self.search([("ranking_date", "=", today)]).unlink()
        Report = self.env["cf.productivity.report"]
        grouped = Report.read_group([("date_time", ">=", datetime.combine(today, datetime.min.time())),
                                     ("date_time", "<=", datetime.combine(today, datetime.max.time()))],
                                    ["user_id"], ["user_id"])
        for g in grouped:
            uid = g["user_id"][0]
            cnt = g["__count"]
            self.create({
                "user_id": uid,
                "ranking_date": today,
                "score": cnt,
                "lines_count": cnt,
            })
        return True
