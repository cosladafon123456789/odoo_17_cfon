
from odoo import models

class ResUsers(models.Model):
    _inherit = "res.users"

    def action_view_productivity(self):
        action = self.env.ref('cf_productivity_report_pro.action_cf_productivity_report').read()[0]
        action['domain'] = [('user_id', 'in', self.ids)]
        return action
