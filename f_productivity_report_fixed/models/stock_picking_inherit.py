# -*- coding: utf-8 -*-
from odoo import models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            try:
                if picking.picking_type_id.code == "outgoing" and picking.state == "done":
                    self.env["cf.productivity.line"].sudo().log_entry(
                        user=self.env.user,
                        type_key="order",
                        reason="Entrega/Pedido validado",
                        ref_model="stock.picking",
                        ref_id=picking.id,
                    )
            except Exception:
                continue
        return res
