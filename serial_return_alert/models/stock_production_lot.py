from odoo import api, fields, models

class StockProductionLot(models.Model):
    _inherit = "stock.lot"

    return_count = fields.Integer(
        string="Veces devuelto",
        compute="_compute_return_count",
        store=False
    )

    has_return_alert = fields.Boolean(
        string="Alerta de devolución",
        compute="_compute_return_count",
        store=False
    )

    @api.depends("move_line_ids")
    def _compute_return_count(self):
        for lot in self:
            # contamos movimientos de entrada desde devoluciones de clientes
            returns = self.env['stock.move.line'].search_count([
                ('lot_id', '=', lot.id),
                ('move_id.picking_id.picking_type_code', '=', 'incoming'),
                ('move_id.origin_returned_move_id', '!=', False)
            ])
            lot.return_count = returns
            lot.has_return_alert = returns >= 2
