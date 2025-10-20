
from odoo import fields, models

class CFProdCleanRanking(models.Model):
    _name = "cf.clean.ranking"
    _description = "CF Clean Ranking"
    _order = "ranking_date desc, score desc"
    _table = "cf_clean_ranking"

    user_id = fields.Many2one("res.users", "Usuario", required=True)
    ranking_date = fields.Date("Fecha", required=True, default=fields.Date.context_today)
    score = fields.Integer("Puntuación", default=0)
    lines_count = fields.Integer("# Validaciones", default=0)
