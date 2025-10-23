from odoo import models, fields

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    bat100 = fields.Boolean(
        string='BAT100',
        related='lot_id.bat100',
        readonly=False,
        store=False,
        help='Marca si el IMEI seleccionado tiene batería al 100% (guardado en el número de serie).'
    )