from odoo import models, fields

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    # Campo relacionado editable: permite marcar/desmarcar y guarda en el lote (IMEI) correspondiente
    bat100 = fields.Boolean(
        string="BAT100",
        related="lot_id.bat100",
        readonly=False,
        store=False,
        help="Marca si el IMEI seleccionado tiene batería al 100% (guardado en el número de serie).",
    )