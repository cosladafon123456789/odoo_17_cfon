
from odoo import models, fields, api

class SendToLocationWizard(models.TransientModel):
    _name = 'send.to.location.wizard'
    _description = 'Send To Location Wizard'

    order_id = fields.Many2one('sale.order', string="Order", required=True)
    location_dest_id = fields.Many2one('stock.location', string="Destination Location", domain=[('usage','=','internal')], required=True)

    def action_confirm(self):
        StockPicking = self.env['stock.picking']
        for wizard in self:
            order = wizard.order_id
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'internal'),
                ('warehouse_id.company_id', '=', order.company_id.id)
            ], limit=1)

            if not picking_type:
                raise ValueError("No internal picking type found.")

            picking = StockPicking.create({
                'picking_type_id': picking_type.id,
                'location_id': picking_type.default_location_src_id.id,
                'location_dest_id': wizard.location_dest_id.id,
                'origin': order.name,
                'partner_id': order.partner_id.id,
            })

            for line in order.order_line:
                move = self.env['stock.move'].create({
                    'name': line.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'picking_id': picking.id,
                    'location_id': picking.location_id.id,
                    'location_dest_id': wizard.location_dest_id.id,
                })
                move._action_confirm()
                move._action_assign()
                for ml in move.move_line_ids:
                    ml.qty_done = ml.product_uom_qty

            picking.button_validate()
            order.message_post(body=f"Enviado a {wizard.location_dest_id.display_name}")
