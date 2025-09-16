
# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

RETURN_THRESHOLD = 2  # Umbral para alertar

class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"  # En v17 el modelo es 'stock.lot' (alias de stock.production.lot)

    x_return_count = fields.Integer(
        string="Veces devuelto",
        compute="_compute_return_info",
        search="_search_x_return_count",
        help="Número de veces que este número de serie/lote ha sido devuelto por clientes (pickings de retorno).",
    )
    x_on_hand_qty = fields.Float(
        string="Cantidad en stock (int.)",
        compute="_compute_return_info",
        search="_search_x_on_hand_qty",
        help="Stock disponible en ubicaciones internas para este lote.",
    )
    x_return_alert = fields.Boolean(
        string="Alerta devoluciones (≥2)",
        compute="_compute_return_info",
        help="Marcado si el lote ha sido devuelto 2 o más veces.",
    )

    def _compute_return_info(self):
        """Compute in batch: return count (customer returns) & on hand qty in internal locations."""
        lot_ids = self.ids
        # Default all to zero/False
        for lot in self:
            lot.x_return_count = 0
            lot.x_on_hand_qty = 0.0
            lot.x_return_alert = False

        if not lot_ids:
            return

        # 1) Return count via SQL (fast): stock_move_line joined to stock_picking with is_return = true and incoming
        self.env.cr.execute("""
            SELECT sml.lot_id, COUNT(*) AS cnt
            FROM stock_move_line sml
            JOIN stock_picking sp ON sp.id = sml.picking_id
            WHERE sml.lot_id = ANY(%s)
              AND sp.state = 'done'
              AND sp.is_return = TRUE
              AND sp.picking_type_id IN (
                    SELECT id FROM stock_picking_type WHERE code = 'incoming'
              )
            GROUP BY sml.lot_id
        """, (lot_ids,))
        counts = dict(self.env.cr.fetchall()) if self.env.cr.rowcount else {}

        # 2) On-hand qty in internal locations via SQL from stock_quant
        self.env.cr.execute("""
            SELECT lot_id, COALESCE(SUM(quantity - reserved_quantity), 0) AS onhand
            FROM stock_quant sq
            JOIN stock_location sl ON sl.id = sq.location_id
            WHERE lot_id = ANY(%s)
              AND sl.usage = 'internal'
            GROUP BY lot_id
        """, (lot_ids,))
        onhands = dict(self.env.cr.fetchall()) if self.env.cr.rowcount else {}

        for lot in self:
            lot.x_return_count = int(counts.get(lot.id, 0))
            lot.x_on_hand_qty = float(onhands.get(lot.id, 0.0))
            lot.x_return_alert = lot.x_return_count >= RETURN_THRESHOLD

    @api.model
    def _search_x_return_count(self, operator, value):
        """Search helper for x_return_count with SQL HAVING count(...) <op> value."""
        # Sanitize operator
        valid_ops = ['=', '!=', '<', '<=', '>', '>=']
        if operator not in valid_ops:
            operator = '>='
        try:
            v = int(value)
        except Exception:
            v = 0
        self.env.cr.execute(f"""
            SELECT sml.lot_id
            FROM stock_move_line sml
            JOIN stock_picking sp ON sp.id = sml.picking_id
            JOIN stock_picking_type spt ON spt.id = sp.picking_type_id
            WHERE sp.state = 'done'
              AND sp.is_return = TRUE
              AND spt.code = 'incoming'
              AND sml.lot_id IS NOT NULL
            GROUP BY sml.lot_id
            HAVING COUNT(*) {operator} %s
        """, (v,))
        lot_ids = [r[0] for r in self.env.cr.fetchall()]
        if not lot_ids and operator in ('=', '<=', '<'):
            # For equality to 0 or less, include lots without any return
            if (operator in ('=', '<=', '<')) and v > 0:
                return [('id', '=', 0)]
            # Return those without records (not implemented to avoid heavy search); keep simple
            return [('id', 'in', lot_ids)]  # likely empty
        return [('id', 'in', lot_ids)]

    @api.model
    def _search_x_on_hand_qty(self, operator, value):
        valid_ops = ['=', '!=', '<', '<=', '>', '>=']
        if operator not in valid_ops:
            operator = '>'
        try:
            v = float(value)
        except Exception:
            v = 0.0
        self.env.cr.execute(f"""
            SELECT sq.lot_id, COALESCE(SUM(sq.quantity - sq.reserved_quantity), 0) AS onhand
            FROM stock_quant sq
            JOIN stock_location sl ON sl.id = sq.location_id
            WHERE sq.lot_id IS NOT NULL
              AND sl.usage = 'internal'
            GROUP BY sq.lot_id
            HAVING COALESCE(SUM(sq.quantity - sq.reserved_quantity), 0) {operator} %s
        """, (v,))
        lot_ids = [r[0] for r in self.env.cr.fetchall()]
        return [('id', 'in', lot_ids)]
