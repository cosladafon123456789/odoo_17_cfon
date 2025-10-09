from odoo import models
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        """Envía status=11 a Laravel solo al confirmar una factura rectificativa (out_refund)."""
        res = super(AccountMove, self).action_post()

        for move in self:
            if move.move_type == 'out_refund':  # Solo notas de crédito de cliente
                try:
                    sale_order = move.invoice_origin and self.env['sale.order'].search(
                        [('name', '=', move.invoice_origin)], limit=1
                    )
                    if sale_order:
                        sale_order._notify_delivery_status(status=11)
                        _logger.info(
                            f"✔ Factura rectificativa {move.name} confirmada. "
                            f"Pedido {sale_order.name} → status 11 enviado a Laravel."
                        )
                    else:
                        _logger.info(f"Factura rectificativa {move.name} confirmada (sin pedido vinculado).")
                except Exception as e:
                    _logger.error(f"❌ Error notificando status 11 a Laravel desde factura rectificativa {move.name}: {e}")

        return res
