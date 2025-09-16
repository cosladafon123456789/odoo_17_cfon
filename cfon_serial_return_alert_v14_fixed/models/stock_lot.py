
# -*- coding: utf-8 -*-
from odoo import api, fields, models

RETURN_THRESHOLD = 2  # Cambia este valor si quieres otro umbral

class StockLotReturnAlert(models.Model):
    _inherit = "stock.lot"  # En Odoo 17 el modelo es 'stock.lot'

    x_return_count = fields.Integer(
        string="Veces devuelto",
        compute="_compute_return_info",
        help="Número de veces que este número de serie/lote ha sido devuelto por clientes (retornos de ventas finalizados).",
    )
    x_on_hand_qty = fields.Float(
        string="Stock interno",
        compute="_compute_return_info",
        help="Stock disponible en ubicaciones internas para este lote.",
    )
    x_return_alert = fields.Boolean(
        string="Alerta devoluciones (≥2)",
        compute="_compute_return_info",
        help="Marcado si el lote ha sido devuelto 2 o más veces.",
    )

    def _compute_return_info(self):
        lot_ids = self.ids
        for lot in self:
            lot.x_return_count = 0
            lot.x_on_hand_qty = 0.0
            lot.x_return_alert = False
        if not lot_ids:
            return

        # Comprobar si existe la columna is_return en stock_picking
        self.env.cr.execute("""
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'stock_picking' AND column_name = 'is_return'
            LIMIT 1
        """)
        has_is_return = bool(self.env.cr.fetchone())

        if has_is_return:
            self.env.cr.execute("""
                SELECT sml.lot_id, COUNT(*) AS cnt
                FROM stock_move_line sml
                JOIN stock_move sm ON sm.id = sml.move_id
                JOIN stock_picking sp ON sp.id = sml.picking_id
                JOIN stock_picking_type spt ON spt.id = sp.picking_type_id
                WHERE sml.lot_id = ANY(%s)
                  AND sp.state = 'done'
                  AND spt.code = 'incoming'
                  AND (sp.is_return = TRUE OR sm.origin_returned_move_id IS NOT NULL)
                GROUP BY sml.lot_id
            """, (lot_ids,))
        else:
            # Fallback sin is_return: entradas 'incoming' provenientes de devoluciones o cuyo nombre/tipo contiene 'return'/'devol'
            self.env.cr.execute("""
                SELECT sml.lot_id, COUNT(*) AS cnt
                FROM stock_move_line sml
                JOIN stock_move sm ON sm.id = sml.move_id
                JOIN stock_picking sp ON sp.id = sml.picking_id
                JOIN stock_picking_type spt ON spt.id = sp.picking_type_id
                WHERE sml.lot_id = ANY(%s)
                  AND sp.state = 'done'
                  AND spt.code = 'incoming'
                  AND (
                        sm.origin_returned_move_id IS NOT NULL
                        OR lower(spt.name) LIKE '%%return%%'
                        OR lower(spt.name) LIKE '%%devol%%'
                        OR lower(COALESCE(sp.name, '')) LIKE '%%return%%'
                        OR lower(COALESCE(sp.name, '')) LIKE '%%devol%%'
                  )
                GROUP BY sml.lot_id
            """, (lot_ids,))

        counts = dict(self.env.cr.fetchall() or [])

        # Stock disponible en internas
        self.env.cr.execute("""
            SELECT lot_id, COALESCE(SUM(quantity - reserved_quantity), 0) AS onhand
            FROM stock_quant sq
            JOIN stock_location sl ON sl.id = sq.location_id
            WHERE lot_id = ANY(%s)
              AND sl.usage = 'internal'
            GROUP BY lot_id
        """, (lot_ids,))
        onhands = dict(self.env.cr.fetchall() or [])

        for lot in self:
            cnt = int(counts.get(lot.id, 0))
            oh = float(onhands.get(lot.id, 0.0))
            lot.x_return_count = cnt
            lot.x_on_hand_qty = oh
            lot.x_return_alert = cnt >= RETURN_THRESHOLD
