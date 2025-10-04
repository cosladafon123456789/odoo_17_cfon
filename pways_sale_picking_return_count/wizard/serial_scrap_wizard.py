from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class RepairActionWizard(models.TransientModel):
    _inherit = 'repair.action.wizard'

    has_serials_with_multiple_returns = fields.Boolean(string="Has Problematic Serials",compute="_compute_has_serials_with_multiple_returns")

    @api.depends('line_ids.lot_id')
    def _compute_has_serials_with_multiple_returns(self):
        for wizard in self:
            wizard.has_serials_with_multiple_returns = any(
                line.lot_id and line.lot_id.return_count >= 2
                for line in wizard.line_ids)


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



class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    has_problematic_batch = fields.Boolean(
        string="Problematic Batch",
        compute="_compute_has_problematic_batch"
    )

    @api.depends('product_return_moves')
    def _compute_has_problematic_batch(self):
        for line in self:
            line.has_problematic_batch = any(
                ml.lot_id and ml.lot_id.return_count >= 2
                for ml in line.product_return_moves.mapped('move_id.move_line_ids'))