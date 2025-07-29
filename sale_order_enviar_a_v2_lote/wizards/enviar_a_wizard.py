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

        for line in order.order_line:
            product = line.product_id
            qty = int(line.product_uom_qty)

            move = self.env['stock.move'].create({
                'name': line.name,
                'product_id': product.id,
                'product_uom_qty': qty,
                'product_uom': line.product_uom.id,
                'location_id': location_src.id,
                'location_dest_id': self.location_id.id,
                'picking_id': picking.id,
            })

            if product.tracking != 'none':
                # Buscar los IMEIs disponibles exactamente en WH/Stock
                available_lots = self.env['stock.quant'].search([
                    ('product_id', '=', product.id),
                    ('location_id', '=', location_src.id),
                    ('quantity', '>=', 1),
                    ('lot_id', '!=', False),
                ])

                for i in range(min(qty, len(available_lots))):
                    self.env['stock.move.line'].create({
                        'move_id': move.id,
                        'product_id': product.id,
                        'product_uom_id': product.uom_id.id,
                        'qty_done': 1,
                        'location_id': location_src.id,
                        'location_dest_id': self.location_id.id,
                        'picking_id': picking.id,
                        'lot_id': available_lots[i].lot_id.id,
                    })

                # Si hay menos IMEIs disponibles que cantidad requerida, crear líneas vacías
                for _ in range(qty - len(available_lots)):
                    self.env['stock.move.line'].create({
                        'move_id': move.id,
                        'product_id': product.id,
                        'product_uom_id': product.uom_id.id,
                        'qty_done': 1,
                        'location_id': location_src.id,
                        'location_dest_id': self.location_id.id,
                        'picking_id': picking.id,
                        'lot_id': False,  # Para que puedas elegirlo manualmente
                    })
            else:
                # Producto sin seguimiento
                self.env['stock.move.line'].create({
                    'move_id': move.id,
                    'product_id': product.id,
                    'product_uom_id': product.uom_id.id,
                    'qty_done': qty,
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
