
from odoo import api, fields, models
from datetime import datetime, date

class CFProductivityRanking(models.Model):
    _name = "cf.productivity.ranking"
    _description = "CF Productivity Ranking"
    _order = "ranking_date desc, score desc"

    user_id = fields.Many2one("res.users", string="Usuario", required=True)
    ranking_date = fields.Date(string="Fecha", required=True, default=fields.Date.context_today)
    score = fields.Integer(string="Puntuación", default=0)
    lines_count = fields.Integer(string="# Validaciones", default=0)

    def action_rebuild_today(self):
        today = fields.Date.context_today(self)
        # Simple scoring: # of report lines today per user
        Report = self.env["cf.productivity.report"]
        self.search([("ranking_date", "=", today)]).unlink()
        data = self.env["cf.productivity.report"].read_group(
            domain=[("date_time", ">=", datetime.combine(today, datetime.min.time())),
                    ("date_time", "<=", datetime.combine(today, datetime.max.time()))],
            fields=["user_id"],
            groupby=["user_id"],
        )
        for row in data:
            user = row.get("user_id") and row["user_id"][0] or False
            cnt = row.get("__count", 0)
            self.create({
                "user_id": user,
                "ranking_date": today,
                "score": cnt,
                "lines_count": cnt,
            })
        return True
