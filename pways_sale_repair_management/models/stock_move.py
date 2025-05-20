from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date

class StockMove(models.Model):
    _inherit = 'stock.move'

    date_force_expiry = fields.Date('Expiry Date')

    # @api.model
    # def _default_vendor_location(self):
    #     return self.env['stock.location'].search([
    #         ('usage', '=', 'supplier'),
    #         ('return_location', '=', True)], limit=1)

class StockQuantInherit(models.Model):
    _inherit = 'stock.quant'

    rma_transfer_move_id = fields.Many2one("stock.move", "RMA transfer move")

    @api.model
    def create_internal_picking_for_tracked_products_quant(self):
        today = date.today()

        rma_location = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1).rma_location

        if not rma_location:
            raise ValidationError(_("You need to fill RMA Location in Warehouse"))

        expiration_date = self.lot_id.expiration_date

        quants = self.search([
            ('lot_id.expiration_date', '<=', today),
            ('product_id.tracking', '!=', 'none'),
            ("location_id.usage", "=", "internal"),
            ('rma_transfer_move_id', '=', False)
        ])


        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'internal')], limit=1)

        for quant in quants:
            picking = self.env['stock.picking'].create({
                'picking_type_id': picking_type.id,
                'location_id': quant.location_id.id,
                'location_dest_id': rma_location.id,
                'move_type': 'direct',
                'origin': f'Auto-Picking for {quant.product_id.display_name}',
            })

            move = self.env['stock.move'].create({
                'name': quant.product_id.display_name,
                'product_id': quant.product_id.id,
                'product_uom': quant.product_uom_id.id,
                'product_uom_qty': quant.quantity,
                'picking_id': picking.id,
                'location_id': quant.location_id.id,
                'location_dest_id': rma_location.id,
                'company_id': quant.company_id.id,
                'date': fields.Datetime.now(),
            })

            self.env['stock.move.line'].create({
                'move_id': move.id,
                'picking_id': picking.id,
                'product_id': quant.product_id.id,
                'product_uom_id': quant.product_uom_id.id,
                'quantity': quant.quantity,
                'location_id': quant.location_id.id,
                'location_dest_id': rma_location.id,
                'lot_id': quant.lot_id.id,
            })
            quant.rma_transfer_move_id = move.id
            print('picking>>>>>>>>>>>>',picking.name)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.depends('product_id', 'picking_type_use_create_lots', 'lot_id.expiration_date')
    def _compute_expiration_date(self):
        for move_line in self:
            if move_line.move_id.date_force_expiry:
                move_line.expiration_date = move_line.move_id.date_force_expiry
            else:
                if not move_line.expiration_date and move_line.lot_id.expiration_date:
                    move_line.expiration_date = move_line.lot_id.expiration_date
                elif move_line.picking_type_use_create_lots:
                    if move_line.product_id.use_expiration_date:
                        if not move_line.expiration_date:
                            move_line.expiration_date = fields.Datetime.today() + datetime.timedelta(days=move_line.product_id.expiration_time)
                    else:
                        move_line.expiration_date = False
