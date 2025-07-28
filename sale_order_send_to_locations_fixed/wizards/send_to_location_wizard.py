
from odoo import models, fields, api

class SendToLocationWizard(models.TransientModel):
    _name = 'send.to.location.wizard'
    _description = 'Send To Location Wizard'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    location_id = fields.Many2one('stock.location', string='Ubicación destino', required=True)

    def action_confirm(self):
        self.ensure_one()
        sale_order = self.sale_order_id
        picking_type = self.env.ref('stock.picking_type_out')  # entrega

        picking = self.env['stock.picking'].create({
            'partner_id': sale_order.partner_id.id,
            'picking_type_id': picking_type.id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': self.location_id.id,
            'origin': sale_order.name,
        })

        for line in sale_order.order_line:
            if not line.product_id:
                continue
            move = self.env['stock.move'].create({
                'name': line.name,
                'product_id': line.product_id.id,
                'product_uom': line.product_uom.id,
                'product_uom_qty': line.product_uom_qty,
                'picking_id': picking.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
            })
            move._action_confirm()
            move._action_assign()
            for ml in move.move_line_ids:
                ml.qty_done = move.product_uom_qty

        picking.button_validate()
        sale_order.message_post(body=f"Productos enviados a {self.location_id.display_name}.")
