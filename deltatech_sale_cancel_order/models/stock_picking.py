# ©  2008-now Terrabit
# See README.rst file on addons root folder for license details


from odoo import _, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    cancel_requested = fields.Boolean("Cancel requested", default=False)

    def button_validate(self):
        for picking in self:
            if picking.cancel_requested:
                raise UserError(_(f"Cannot validate {picking.name}, order with cancel requested"))
        return super().button_validate()
