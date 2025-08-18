from odoo import models

class StockPickingNoExpiry(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        # Flags de contexto comunes usados por módulos de caducidad
        ctx = dict(self.env.context or {})
        ctx.update({
            'skip_expiry_check': True,
            'ignore_expiration': True,
            'no_expiration_popup': True,
        })
        self = self.with_context(ctx)
        # Intento de validación normal respetando el contexto
        try:
            return super(StockPickingNoExpiry, self).button_validate()
        except Exception:
            # Plan B: validación directa si algún asistente lanza excepción
            self._action_done()
            return self.action_view_picking()
