from odoo import models

class StockWarnExpirationNoPopup(models.TransientModel):
    _inherit = 'stock.warn.expiration'

    def action_confirm(self):
        return {'type': 'ir.actions.act_window_close'}

    def action_confirm_except_expired(self):
        return {'type': 'ir.actions.act_window_close'}
