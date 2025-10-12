# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        # Before calling super, we capture if should count
        count_it = False
        company = self.env.company
        if company.cf_user_order_id and company.cf_user_order_id.id == self.env.user.id:
            # Count only deliveries (ventas)
            if any(picking.picking_type_code == "outgoing" for picking in self):
                count_it = True
        res = super().button_validate()
        if count_it:
            for picking in self.filtered(lambda p: p.picking_type_code == "outgoing"):
                self.env["cf.productivity.line"].sudo().log_entry(
                    user=self.env.user,
                    type_key="order",
                    reason=None,
                    ref_model="stock.picking",
                    ref_id=picking.id,
                )
        return res