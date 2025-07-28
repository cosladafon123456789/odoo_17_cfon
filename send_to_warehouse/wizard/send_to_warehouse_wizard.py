from odoo import api, fields, models
from odoo.exceptions import UserError

class SendToWarehouseWizard(models.TransientModel):
    _name = 'send.to.warehouse.wizard'
    _description = 'Send to Warehouse Wizard'

    warehouse_id = fields.Many2one('stock.warehouse', string='Destino', required=True)

    def confirm_transfer(self):
        sale_order = self.env['sale.order'].browse(self.env.context.get('active_id'))
        if not sale_order:
            raise UserError("No hay orden de venta activa.")

        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            ('warehouse_id', '=', sale_order.warehouse_id.id)
        ], limit=1)

        if not picking_type:
            raise UserError("No se encontró tipo de traslado interno para el almacén de origen.")

        destination_location = self.warehouse_id.lot_stock_id

        for line in sale_order.order_line:
            self.env['stock.picking'].create({
                'picking_type_id': picking_type.id,
                'location_id': picking_type.default_location_src_id.id,
                'location_dest_id': destination_location.id,
                'origin': sale_order.name,
                'move_ids_without_package': [(0, 0, {
                    'name': line.name,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom.id,
                    'product_uom_qty': line.product_uom_qty,
                    'location_id': picking_type.default_location_src_id.id,
                    'location_dest_id': destination_location.id,
                })]
            })