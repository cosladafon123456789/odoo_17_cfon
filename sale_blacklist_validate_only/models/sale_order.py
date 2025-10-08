from odoo import models

class SaleOrder(models.Model):
    _inherit = "sale.order"
    # Ya no se realiza ninguna comprobación aquí (solo al validar entrega).
