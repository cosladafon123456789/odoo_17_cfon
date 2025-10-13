
# -*- coding: utf-8 -*-
from odoo import models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            try:
                if picking.picking_type_id.code == "outgoing":
                    company_user = self.env.company.cf_user_order_id or self.env.user
                    self.env["cf.productivity.line"].sudo().log_entry(
                        user=company_user,
                        type_key="order",
                        reason="Entrega/Pedido validado",
                        ref_model="stock.picking",
                        ref_id=picking.id,
                    )
            except Exception:
                continue
        return res
