
from odoo import api, fields, models

class StockProductionLot(models.Model):
    _inherit = "stock.lot"

    # Campos no almacenados; se calculan bajo demanda
    return_count = fields.Integer(
        string="Veces devuelto",
        compute="_compute_return_stats",
        store=False
    )
    has_return_alert = fields.Boolean(
        string="Alerta de devolución",
        compute="_compute_return_stats",
        store=False
    )

    # Sin @api.depends para evitar dependencias inexistentes; se evalúa on-the-fly
    def _compute_return_stats(self):
        StockMoveLine = self.env['stock.move.line']
        for lot in self:
            if not lot.id:
                lot.return_count = 0
                lot.has_return_alert = False
                continue
            returns = StockMoveLine.search_count([
                ('lot_id', '=', lot.id),
                ('move_id.picking_id.picking_type_code', '=', 'incoming'),
                ('move_id.origin_returned_move_id', '!=', False),
            ])
            lot.return_count = returns
            lot.has_return_alert = returns >= 2
