from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta
import datetime

class PurchaseOrder(models.Model):
	_inherit = "purchase.order"

	repair_id = fields.Many2one('repair.order')

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	stock_lot_id = fields.Many2one('stock.lot')


class RepairOrder(models.Model):
	_inherit = 'repair.order'

	stock_lot_id = fields.Many2one('stock.lot')
	purchase_count = fields.Integer(compute='compute_purchase_count')

	def compute_purchase_count(self):
		for rec in self:
			purchase_ids = self.env['purchase.order'].search([('repair_id', '=', self.id)])
			rec.purchase_count = len(purchase_ids.ids)

	def button_view_purchase(self):
		check_ids = self.env['purchase.order'].search([('repair_id', '=', self.id)])
		return {
			'name': _('Purchase'),
			'binding_view_types': 'form',
			'view_mode': 'list,form',
			'res_model': 'purchase.order',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', check_ids.ids)],
		}

	def action_create_purchase_order(self):
		self.ensure_one()
		supplier = self.partner_id

		po_lines_vals = []
		for move in self.move_ids:
			if (
				move.repair_line_type == 'add'
				and move.qty_available < move.product_uom_qty
			):
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
			return

		po_vals = {
			'partner_id': supplier.id,
			'order_line': po_lines_vals,
			'origin': self.name,
			'repair_id': self.id
		}
		po = self.env['purchase.order'].create(po_vals)
		return {
			'type': 'ir.actions.act_window',
			'name': 'Purchase Order',
			'res_model': 'purchase.order',
			'view_mode': 'form',
			'res_id': po.id,
		}



class StockMove(models.Model):
	_inherit = 'stock.move'

	qty_available = fields.Float(related='product_id.qty_available')

	# @api.onchange('product_id')
	# def _onchange_qty_available(self):
	# 	for ro in self:
	# 		print('Caleed>>>>>>>>>>>>')
	# 		ro.warranty_period = po.partner_id.warranty_period or 0.0