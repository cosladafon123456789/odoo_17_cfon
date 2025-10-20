
from odoo import fields, models

class CFProdCleanStats(models.Model):
    _name = "cf.clean.stats"
    _description = "CF Clean Stats"
    _order = "create_date desc"
    _table = "cf_clean_stats"

    name = fields.Char("Nombre", required=True, default="Estadística")
    user_id = fields.Many2one("res.users", "Usuario")
    avg_interval = fields.Char("Tiempo medio")
