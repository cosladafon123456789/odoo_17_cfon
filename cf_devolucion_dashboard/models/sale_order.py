from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    fecha_devolucion = fields.Datetime(string="Fecha de devolución", copy=False, tracking=True)