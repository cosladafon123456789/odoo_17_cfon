from odoo import models, _


class StockPicking(models.Model):
    _inherit = "stock.picking"


    def _action_generate_expired_wizard(self):
        return True
