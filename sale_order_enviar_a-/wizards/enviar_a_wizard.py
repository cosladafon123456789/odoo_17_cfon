from odoo import models, fields

class EnviarAWizard(models.TransientModel):
    _name = 'enviar.a.wizard'
    _description = 'Enviar productos a otra ubicación'

    order_id = fields.Many2one('sale.order', string='Pedido de venta', required=True)
    location_id = fields.Many2one('stock.location', string='Ubicación destino', required=True)

    def action_enviar_producto(self):
        picking_type = self.env.ref('stock.picking_type_internal')
        order = self.order_id

        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': order.warehouse_id.lot_stock_id.id,
            'location_dest_id': self.location_id.id,
            'origin': order.name,
            'move_ids_without_package': [
                (0, 0, {
                    'name': line.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'location_id': order.warehouse_id.lot_stock_id.id,
                    'location_dest_id': self.location_id.id,
                }) for line in order.order_line
            ]
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': picking.id,
            'view_mode': 'form',
            'target': 'current',
        }
