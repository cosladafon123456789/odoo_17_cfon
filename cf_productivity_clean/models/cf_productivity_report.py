
from odoo import api, fields, models

class CFProdCleanReport(models.Model):
    _name = "cf.clean.report"
    _description = "CF Clean Productivity Report"
    _order = "date_time asc"
    _table = "cf_clean_report"

    name = fields.Char("Descripción", required=True, default="Validación")
    user_id = fields.Many2one("res.users", "Usuario", required=True, default=lambda self: self.env.user)
    date_time = fields.Datetime("Fecha/Hora", default=fields.Datetime.now, required=True)
    reason = fields.Char("Motivo")
    action_type = fields.Selection([("picking_validate", "Validación"), ("other", "Otro")], default="picking_validate")
