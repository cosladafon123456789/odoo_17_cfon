
# -*- coding: utf-8 -*-
from odoo import fields, models, tools

class CfonLotReturnReport(models.Model):
    _name = "cfon.lot_return_report"
    _description = "CFON - Lotes con 2+ devoluciones y stock"
    _auto = False
    _order = "return_count desc, lot_id"
    _rec_name = "lot_id"

    lot_id = fields.Many2one("stock.lot", string="Lote/Nº Serie", readonly=True)
    return_count = fields.Integer("Veces devuelto", readonly=True)
    on_hand_qty = fields.Float("Stock interno", readonly=True)
    alert = fields.Boolean("Alerta (≥2)", readonly=True)

    def init(self):
        cr = self._cr
        tools.drop_view_if_exists(cr, "cfon_lot_return_report")

        # ¿Existe stock_picking.is_return?
        cr.execute("""
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'stock_picking' AND column_name = 'is_return'
            LIMIT 1
        """)
        has_is_return = bool(cr.fetchone())

        return_filter = """
              AND (sp.is_return = TRUE OR sm.origin_returned_move_id IS NOT NULL)
        """ if has_is_return else """
              AND (
                    sm.origin_returned_move_id IS NOT NULL
                    OR lower(spt.name) LIKE '%%return%%' OR lower(spt.name) LIKE '%%devol%%'
                    OR lower(COALESCE(sp.name, '')) LIKE '%%return%%' OR lower(COALESCE(sp.name, '')) LIKE '%%devol%%'
              )
        """

        view_sql = f"""
        CREATE VIEW cfon_lot_return_report AS
        WITH ret AS (
            SELECT sml.lot_id, COUNT(*)::integer AS return_count
            FROM stock_move_line sml
            JOIN stock_move sm ON sm.id = sml.move_id
            JOIN stock_picking sp ON sp.id = sml.picking_id
            JOIN stock_picking_type spt ON spt.id = sp.picking_type_id
            WHERE sml.lot_id IS NOT NULL
              AND sp.state = 'done'
              AND spt.code = 'incoming'
              {return_filter}
            GROUP BY sml.lot_id
        ),
        onhand AS (
            SELECT sq.lot_id, COALESCE(SUM(sq.quantity - sq.reserved_quantity), 0.0) AS on_hand_qty
            FROM stock_quant sq
            JOIN stock_location sl ON sl.id = sq.location_id
            WHERE sq.lot_id IS NOT NULL
              AND sl.usage = 'internal'
            GROUP BY sq.lot_id
        )
        SELECT
            COALESCE(r.lot_id, o.lot_id) AS id,
            COALESCE(r.lot_id, o.lot_id) AS lot_id,
            COALESCE(r.return_count, 0) AS return_count,
            COALESCE(o.on_hand_qty, 0.0) AS on_hand_qty,
            (COALESCE(r.return_count, 0) >= 2) AS alert
        FROM ret r
        FULL JOIN onhand o ON o.lot_id = r.lot_id
        WHERE COALESCE(r.return_count, 0) >= 2
          AND COALESCE(o.on_hand_qty, 0) > 0;
        """
        cr.execute(view_sql)
