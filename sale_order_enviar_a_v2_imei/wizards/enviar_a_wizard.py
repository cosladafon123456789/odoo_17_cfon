from odoo import models, fields

class EnviarAWizard(models.TransientModel):
    _name = 'enviar.a.wizard'
    _description = 'Enviar productos a otra ubicación'

    order_id = fields.Many2one('sale.order', string='Pedido de venta', required=True)
    location_id = fields.Many2one('stock.location', string='Ubicación destino', required=True)

    def action_enviar_producto(self):
        StockPicking = self.env['stock.picking']
        StockMoveLine = self.env['stock.move.line']
        StockMove = self.env['stock.move']
        Quant = self.env['stock.quant']

        picking_type_internal = self.env.ref('stock.picking_type_internal')
        picking_type_in = self.env.ref('stock.picking_type_in')

        order = self.order_id
        location_stock = order.warehouse_id.lot_stock_id

        send_picking = None

        for line in order.order_line:
            product = line.product_id
            qty = int(line.product_uom_qty)

            # Buscar movimientos de salida hechos desde el pedido original con IMEI asignado
            outgoing_move_lines = StockMoveLine.search([
                ('picking_id.origin', '=', order.name),
                ('product_id', '=', product.id),
                ('lot_id', '!=', False),
                ('location_dest_id.usage', '=', 'customer'),
                ('picking_id.state', '=', 'done')
            ])

            exact_lots = outgoing_move_lines.mapped('lot_id')

            # Hacer devolución de cada IMEI exacto
            for lot in exact_lots:
                return_picking = StockPicking.create({
                    'picking_type_id': picking_type_in.id,
                    'location_id': lot.quant_ids.filtered(lambda q: q.location_id.usage == 'customer').location_id.id,
                    'location_dest_id': location_stock.id,
                    'origin': f'Devolución automática de {order.name}',
                })

                move = StockMove.create({
                    'name': product.name,
                    'product_id': product.id,
                    'product_uom_qty': 1,
                    'product_uom': product.uom_id.id,
                    'location_id': return_picking.location_id.id,
                    'location_dest_id': location_stock.id,
                    'picking_id': return_picking.id,
                })

                StockMoveLine.create({
                    'product_id': product.id,
                    'product_uom_id': product.uom_id.id,
                    'qty_done': 1,
                    'lot_id': lot.id,
                    'location_id': return_picking.location_id.id,
                    'location_dest_id': location_stock.id,
                    'picking_id': return_picking.id,
                    'move_id': move.id,
                })

                return_picking.action_confirm()
                return_picking.button_validate()

            # Crear traslado a nueva ubicación
            send_picking = StockPicking.create({
                'picking_type_id': picking_type_internal.id,
                'location_id': location_stock.id,
                'location_dest_id': self.location_id.id,
                'origin': order.name,
            })

            move = StockMove.create({
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': len(exact_lots),
                'product_uom': product.uom_id.id,
                'location_id': location_stock.id,
                'location_dest_id': self.location_id.id,
                'picking_id': send_picking.id,
            })

            for lot in exact_lots:
                StockMoveLine.create({
                    'move_id': move.id,
                    'product_id': product.id,
                    'product_uom_id': product.uom_id.id,
                    'qty_done': 1,
                    'location_id': location_stock.id,
                    'location_dest_id': self.location_id.id,
                    'picking_id': send_picking.id,
                    'lot_id': lot.id,
                })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': send_picking.id if send_picking else False,
            'view_mode': 'form',
            'target': 'current',
        }
