from odoo import models

class StockPickingNoExpiry(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        ctx = dict(self.env.context or {})
        ctx.update({
            'skip_expiry_check': True,
            'ignore_expiration': True,
            'no_stock_warn_expiration': True,
            'no_expiration_popup': True,
        })
        self = self.with_context(ctx)
        for picking in self:
            picking.action_assign()
        try:
            return super(StockPickingNoExpiry, self).button_validate()
        except Exception:
            self._action_done()
            return self.action_view_picking()
