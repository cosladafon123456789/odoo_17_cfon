from odoo import _, api, Command, fields, models
from odoo.tools.float_utils import float_round, float_is_zero
from odoo.exceptions import ValidationError,UserError
from datetime import date, timedelta
import datetime

class PurchaseOrder(models.Model):
	_inherit = "purchase.order"

	repair_id = fields.Many2one('repair.order')

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	stock_lot_id = fields.Many2one('stock.lot')

class StockWarehouse(models.Model):
	_inherit = 'stock.warehouse'

	repair_loc_id = fields.Many2one('stock.location', string='Repair Location')


class RepairOrder(models.Model):
	_inherit = 'repair.order'

	stock_lot_id = fields.Many2one('stock.lot')
	stock_picking_id = fields.Many2one('stock.picking')
	purchase_count = fields.Integer(compute='compute_purchase_count')
	vendor_ids = fields.Many2many('res.partner', string='Vendor')

	def _prepare_move_default_values(self, return_line, new_picking):
		picking = new_picking or return_line.wizard_id.picking_id
		vals = {
			'name': picking.name,
			'product_id': return_line.product_id.id,
			'product_uom_qty': return_line.quantity,
			'product_uom': return_line.product_id.uom_id.id,
			'picking_id': picking.id,
			'state': 'draft',
			'date': fields.Datetime.now(),
			'location_id': return_line.move_id.location_dest_id.id,
			'location_dest_id': return_line.move_id.location_id.id,
			'picking_type_id': picking.picking_type_id.id,
			'warehouse_id': picking.picking_type_id.warehouse_id.id,
			'origin_returned_move_id': return_line.move_id.id,
			'procure_method': 'make_to_stock',
			'group_id': return_line.wizard_id.picking_id.group_id.id,
		}
		return vals

	def _process_line(self,return_line, new_picking):
		self.ensure_one()
		if not float_is_zero(return_line.quantity, precision_rounding=return_line.uom_id.rounding):
			vals = self._prepare_move_default_values(return_line, new_picking)
			if return_line.move_id:
				new_return_move = return_line.move_id.copy(vals)
				vals = {}
				move_orig_to_link = return_line.move_id.move_dest_ids.returned_move_ids
				# link to original move
				move_orig_to_link |= return_line.move_id
				# link to siblings of original move, if any
				move_orig_to_link |= return_line.move_id\
					.move_dest_ids.filtered(lambda m: m.state not in ('cancel'))\
					.move_orig_ids.filtered(lambda m: m.state not in ('cancel'))
				move_dest_to_link = return_line.move_id.move_orig_ids.returned_move_ids
				move_dest_to_link |= return_line.move_id.move_orig_ids.returned_move_ids\
					.move_orig_ids.filtered(lambda m: m.state not in ('cancel'))\
					.move_dest_ids.filtered(lambda m: m.state not in ('cancel'))
				vals['move_orig_ids'] = [Command.link(m.id) for m in move_orig_to_link]
				vals['move_dest_ids'] = [Command.link(m.id) for m in move_dest_to_link]
				new_return_move.write(vals)
			else:
				move_id = self.env['stock.move'].create(vals)
			return True

	def action_repair_end(self):
		res = super(RepairOrder,self).action_repair_end()
		if self.stock_picking_id:
			return_id = self.env['stock.return.picking'].with_context(active_ids=self.stock_picking_id.ids,
				active_id=self.stock_picking_id.id,active_model='stock.picking').create({})
			if return_id:
				for return_move in return_id.product_return_moves.move_id:
					return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()

				# create new picking for returned products
				new_picking = return_id.picking_id.copy(return_id._prepare_picking_default_values())
				new_picking.user_id = False
				new_picking.message_post_with_source(
					'mail.message_origin_link',
					render_values={'self': new_picking, 'origin': return_id.picking_id},
					subtype_xmlid='mail.mt_note',
				)
				returned_lines = False
				for return_line in return_id.product_return_moves:
					if self._process_line(return_line, new_picking):
						returned_lines = True
				if not returned_lines:
					raise UserError(_("Please specify at least one non-zero quantity."))

				new_picking.action_confirm()
				new_picking.action_assign()
				new_picking.button_validate()
		return res

	def compute_purchase_count(self):
		for rec in self:
			purchase_ids = self.env['purchase.order'].search([('repair_id', '=', self.id)])
			rec.purchase_count = len(purchase_ids.ids)

	def button_view_purchase(self):
		check_ids = self.env['purchase.order'].search([('repair_id', '=', self.id)])
		return {
			'name': _('Purchases'),
			'binding_view_types': 'form',
			'view_mode': 'list,form',
			'res_model': 'purchase.order',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', check_ids.ids)],
		}

	def action_create_purchase_orders(self):
		self.ensure_one()
		if not self.vendor_ids:
			raise ValidationError(_("No Vendor Selected, Kindly Select for creating Purchase Order"))
		po_lines_vals = []
		for move in self.move_ids:
			if (move.repair_line_type == 'add' and move.qty_available < move.product_uom_qty):
				required_qty = move.product_uom_qty - move.qty_available
				po_line_val = (0, 0, {
					'product_id': move.product_id.id,
					'product_qty': required_qty,
					'product_uom': move.product_id.uom_po_id.id,
					'price_unit': move.product_id.standard_price,
					'name': move.product_id.display_name,
					'date_planned': fields.Datetime.now(),
				})
				po_lines_vals.append(po_line_val)

		if not po_lines_vals:
			raise ValidationError(_("No Lines for creating Purchase Order"))
		
		purchase_orders = []
		for vendor in self.vendor_ids:
			po_vals = {
				'partner_id': vendor.id,
				'order_line': list(po_lines_vals),
				'origin': self.name,
				'repair_id': self.id
			}
			po = self.env['purchase.order'].create(po_vals)
			purchase_orders.append(po)

		return True

class StockMove(models.Model):
	_inherit = 'stock.move'

	qty_available = fields.Float(related='product_id.qty_available',string='Available Qty')
