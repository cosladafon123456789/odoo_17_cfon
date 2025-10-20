
from odoo import api, fields, models

class CFProductivityStats(models.Model):
    _name = "cf.productivity.stats"
    _description = "CF Productivity Stats"
    _order = "create_date desc"

    name = fields.Char("Nombre", required=True, default="Estadística diaria")
    user_id = fields.Many2one("res.users", "Usuario")
    avg_interval = fields.Char("Tiempo medio (HH:MM:SS)")

    def action_compute_example(self):
        # Placeholder to compute stats if needed
        return True
