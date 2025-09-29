
# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SaleOrderRefundReasonWizard(models.TransientModel):
    _name = 'sale.order.refund.reason.wizard'
    _description = 'Motivo de reembolso en pedido de venta'

    sale_order_id = fields.Many2one('sale.order', string='Pedido', required=True)

    reason_id = fields.Selection([
        ('no_stock', 'No hay stock'),
        ('no_response', 'Se ha llamado al cliente y no responde'),
        ('client_cancel', 'Cancelación por el cliente antes del envío'),
        ('address_issue', 'No es posible realizar el envío a esa dirección'),
        ('other', 'Otro motivo'),
    ], string='Motivo de reembolso', required=True)
    reason_text = fields.Char('Detalle del otro motivo')

    @api.onchange('reason_id')
    def _onchange_reason_id(self):
        if self.reason_id != 'other':
            self.reason_text = False

    def action_confirm_reason(self):
        self.ensure_one()
        # Guardar en el pedido
        self.sale_order_id.refund_reason_code = self.reason_id
        self.sale_order_id.refund_reason_text = self.reason_text
        # Construir el texto final
        selection = dict(self._fields['reason_id'].selection)
        if self.reason_id == 'other':
            final = (self.reason_text or '').strip() or 'Otro motivo'
        else:
            final = selection.get(self.reason_id, '')
        self.sale_order_id.refund_reason = final

        # Abrir el wizard estándar de reembolso/devolución
        return self.sale_order_id.button_refund_original()
