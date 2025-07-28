from odoo import models, fields, api
from odoo.exceptions import UserError

class SendToLocationWizard(models.TransientModel):
    _name = 'send.to.location.wizard'
    _description = 'Send To Location Wizard'

    location_id = fields.Many2one('stock.location', string='Ubicación de destino', required=True)
    sale_id = fields.Many2one('sale.order', string='Orden de venta')

    def action_confirm(self):
        self.ensure_one()
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            ('warehouse_id', '=', self.sale_id.warehouse_id.id)
        ], limit=1)

        if not picking_type:
            raise UserError("No se encontró un tipo de operación de transferencia interna para este almacén.")

        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': self.location_id.id,
            'origin': self.sale_id.name,
        })

        for line in self.sale_id.order_line:
            if line.product_id.type != 'product':
                continue
            move = self.env['stock.move'].create({
                'name': line.name or line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'picking_id': picking.id,
            })

            move._action_confirm()
            move._action_assign()
            for ml in move.move_line_ids:
                ml.qty_done = ml.product_uom_qty

        picking.action_confirm()
        picking.action_assign()
        picking.button_validate()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': picking.id,
            'view_mode': 'form',
            'target': 'current',
        }
