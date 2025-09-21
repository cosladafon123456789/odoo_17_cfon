from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SerialScrapWizard(models.TransientModel):
    _name = "serial.scrap.wizard"
    _description = "Scrap Lot/Serial Wizard"

    lot_id = fields.Many2one("stock.lot", string="Lot/Serial", required=True)
    product_id = fields.Many2one("product.product", string="Product", related="lot_id.product_id", readonly=True)
    location_id = fields.Many2one("stock.location", string="Location")
    scrap_qty = fields.Float(string="Quantity to Scrap")
    scrap_location_id = fields.Many2one("stock.location", string="Scrap Location",domain=[("scrap_location", "=", True), ("usage", "=", "inventory")])

    @api.onchange("lot_id")
    def _onchange_lot(self):
        if self.lot_id:
            quants = self.lot_id.quant_ids.filtered(lambda q: q.quantity > 0)
            if quants:
                quant = quants[0]
                self.location_id = quant.location_id
                self.scrap_qty = quant.quantity

    def action_scrap_lot(self):
        for wiz in self:
            self.env["stock.scrap"].create({
                "product_id": wiz.product_id.id,
                "lot_id": wiz.lot_id.id,
                "product_uom_id": wiz.product_id.uom_id.id,
                "location_id": wiz.location_id.id,
                "scrap_qty": wiz.scrap_qty,
                "name": f"Scrap for {wiz.lot_id.name}"
            })

        return {"type": "ir.actions.act_window_close"}