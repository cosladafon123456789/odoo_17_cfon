
from odoo import api, fields, models

class CFProductivityStats(models.Model):
    _name = "cf.productivity.stats"
    _description = "CF Productivity Stats"
    _table = "cf_productivity_stats"
    _auto = True

    name = fields.Char(string="Nombre", required=True, default="Estadística diaria")
    user_id = fields.Many2one("res.users", string="Usuario")
    avg_interval = fields.Char(string="Tiempo medio")

    def init(self):
        # eliminar vista antigua si existiera
        self.env.cr.execute("DROP VIEW IF EXISTS cf_productivity_stats;")
