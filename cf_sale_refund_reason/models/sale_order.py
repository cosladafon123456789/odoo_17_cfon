
# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    refund_reason_code = fields.Selection([
        ('no_stock', 'No hay stock'),
        ('no_response', 'Se ha llamado al cliente y no responde'),
        ('client_cancel', 'Cancelación por el cliente antes del envío'),
        ('address_issue', 'No es posible realizar el envío a esa dirección'),
        ('other', 'Otro motivo'),
    ], string='Código motivo del reembolso', tracking=True)
    refund_reason_text = fields.Char('Detalle del otro motivo', tracking=True)
    refund_reason = fields.Char('Motivo de reembolso (final)', tracking=True)

    def action_open_refund_reason_wizard(self):
        self.ensure_one()
        return {
            'name': 'Motivo de Reembolso',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.refund.reason.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'default_reason_id': self.refund_reason_code or False,
                'default_reason_text': self.refund_reason_text or False,
            },
        }

    def button_refund_original(self):
        """Llama al método original del botón reembolsar.
        Mantener esta función separada evita recursión al reemplazar el botón en la vista.
        """
        # Importante: delega en el super del método original si existe.
        # En Odoo 17, asumimos que el método que abre el wizard estándar es button_refund.
        return super(SaleOrder, self).button_refund()
