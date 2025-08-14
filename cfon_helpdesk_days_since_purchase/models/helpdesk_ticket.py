from odoo import api, fields, models

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # Días entre la fecha del pedido (date_order) y la apertura del ticket (create_date)
    days_since_purchase = fields.Integer(
        string='Tiempo transcurrido desde la compra (días)',
        compute='_compute_days_since_purchase',
        store=True,
        help='Días entre la fecha del pedido (date_order) y la apertura del ticket.'
    )

    # Texto de estado según días
    purchase_status_text = fields.Char(
        string='Estado postcompra',
        compute='_compute_purchase_status_text',
        store=False
    )

    @api.depends('linked_sale_order_id.date_order', 'create_date')
    def _compute_days_since_purchase(self):
        for t in self:
            days = 0
            order = getattr(t, 'linked_sale_order_id', False)
            if order and order.date_order and t.create_date:
                order_date = fields.Date.to_date(order.date_order)
                open_date = fields.Date.to_date(t.create_date)
                if order_date and open_date:
                    days = max((open_date - order_date).days, 0)
            t.days_since_purchase = days

    @api.depends('days_since_purchase')
    def _compute_purchase_status_text(self):
        for t in self:
            if (t.days_since_purchase or 0) > 730:
                t.purchase_status_text = "GARANTIA EXPIRADA"
            elif (t.days_since_purchase or 0) > 21:
                t.purchase_status_text = "DESESTIMIENTO EXPIRADO"
            else:
                t.purchase_status_text = ""