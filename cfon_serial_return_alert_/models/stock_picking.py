
# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    x_has_problem_lots = fields.Boolean(
        string="Contiene SN/Lotes con ≥2 devoluciones",
        compute="_compute_has_problem_lots",
        help="Marcado si este albarán contiene al menos un número de serie/lote con 2 o más devoluciones previas.",
    )

    def _compute_has_problem_lots(self):
        for picking in self:
            flagged = False
            for ml in picking.move_line_ids:
                if ml.lot_id and getattr(ml.lot_id, 'x_return_count', 0) >= 2:
                    flagged = True
                    break
            picking.x_has_problem_lots = flagged
