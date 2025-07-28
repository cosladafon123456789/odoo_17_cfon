from odoo import models, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_send_to_telemalaga(self):
        self._create_internal_transfer('TELEMALAGA')

    def action_send_to_clinicphone(self):
        self._create_internal_transfer('CLINICPHONE')

    def _create_internal_transfer(self, location_name):
        location = self.env['stock.location'].search([('name', '=', location_name)], limit=1)
        if not location:
            raise UserError(f"La ubicación '{location_name}' no existe.")

        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            ('warehouse_id', '=', self.warehouse_id.id)
        ], limit=1)

        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': location.id,
            'origin': self.name,
            'move_lines': [(0, 0, {
                'name': line.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'location_id': picking_type.default_location_src_id.id,
                'location_dest_id': location.id,
            }) for line in self.order_line if line.product_id.type != 'service']
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': picking.id,
            'view_mode': 'form',
            'target': 'current',
        }
