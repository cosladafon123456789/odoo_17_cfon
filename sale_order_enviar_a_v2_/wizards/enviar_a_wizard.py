from odoo import models, fields

class EnviarAWizard(models.TransientModel):
    _name = 'enviar.a.wizard'
    _description = 'Enviar productos a otra ubicación'

    order_id = fields.Many2one('sale.order', string='Pedido de venta', required=True)
    location_id = fields.Many2one('stock.location', string='Ubicación destino', required=True)

    def action_enviar_producto(self):
        picking_type = self.env.ref('stock.picking_type_internal')
        order = self.order_id
        location_src = order.warehouse_id.lot_stock_id

        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': location_src.id,
            'location_dest_id': self.location_id.id,
            'origin': order.name,
        })

        move_lines = []

        for line in order.order_line:
            product = line.product_id

            move_vals = {
                'name': line.name,
                'product_id': product.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'location_id': location_src.id,
                'location_dest_id': self.location_id.id,
                'picking_id': picking.id,
            }

            move = self.env['stock.move'].create(move_vals)

            # Si el producto requiere seguimiento (IMEI/serie)
            if product.tracking != 'none':
                # Buscar IMEIs disponibles en la ubicación de origen
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', product.id),
                    ('location_id', '=', location_src.id),
                    ('quantity', '>=', 1),
                    ('lot_id', '!=', False)
                ])

                for i, quant in enumerate(quants):
                    if i >= line.product_uom_qty:
                        break
                    self.env['stock.move.line'].create({
                        'move_id': move.id,
                        'product_id': product.id,
                        'product_uom_id': product.uom_id.id,
                        'qty_done': 1,
                        'location_id': location_src.id,
                        'location_dest_id': self.location_id.id,
                        'lot_id': quant.lot_id.id,
                        'picking_id': picking.id,
                    })
            else:
                # Sin seguimiento
                self.env['stock.move.line'].create({
                    'move_id': move.id,
                    'product_id': product.id,
                    'product_uom_id': product.uom_id.id,
                    'qty_done': line.product_uom_qty,
                    'location_id': location_src.id,
                    'location_dest_id': self.location_id.id,
                    'picking_id': picking.id,
                })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': picking.id,
            'view_mode': 'form',
            'target': 'current',
        }
