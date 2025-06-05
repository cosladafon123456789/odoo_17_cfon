from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date

class StockLot(models.Model):
	_inherit = "stock.lot"

	repair_count = fields.Integer(compute='compute_repair_count')
	rma_count = fields.Integer(compute='compute_rma_count')
	avl_delivery_ids = fields.Many2many('stock.picking', string='Available Deliveries', compute='_compute_avl_delivery_ids', store=False)

	@api.depends('delivery_ids')
	def _compute_avl_delivery_ids(self):
		StockQuant = self.env['stock.quant']
		StockMoveLine = self.env['stock.move.line']

		for lot in self:
			lot.avl_delivery_ids = self.env['stock.picking']

			move_lines = StockMoveLine.search([
				('picking_id', 'in', lot.delivery_ids.ids),
				('lot_id', '=', lot.id)])
			# lambda ml: StockQuant.search_count([
			# 	('product_id', '=', ml.product_id.id),
			# 	('lot_id', '=', ml.lot_id.id),
			# 	('location_id.usage', '=', 'customer'),
			# 	('quantity', '>=', ml.quantity)
			# ]) > 0
			matched_pickings = move_lines.mapped('picking_id')

			lot.avl_delivery_ids = matched_pickings

	def compute_repair_count(self):
		for rec in self:
			repair_ids = self.env['repair.order'].search([('stock_lot_id', '=', self.id)])
			rec.repair_count = len(repair_ids.ids)
	
	def compute_rma_count(self):
		for rec in self:
			rma_ids = self.env['stock.picking'].search([('stock_lot_id', '=', self.id)])
			rec.rma_count = len(rma_ids.ids)

	def button_create_lot_repair(self):
		self.ensure_one()
		
		wizard = self.env['lot.repair.order.wizard'].create({
			'action_type': 'repair',
			'stock_lot_id': self.id,
		})

		return {
			'name': 'Create Repair Order',
			'type': 'ir.actions.act_window',
			'res_model': 'lot.repair.order.wizard',
			'view_mode': 'form',
			'res_id': wizard.id,
			'target': 'new',
			'context': {
				'default_stock_lot_id': self.id,
				'default_action_type': 'repair',
			}
		}

	def button_create_rma(self):
		self.ensure_one()
		
		if not self.avl_delivery_ids:
			raise ValidationError("You Don't have picking to Create RMA")

		wizard = self.env['lot.repair.order.wizard'].create({
			'action_type': 'rma',
			'stock_lot_id': self.id,
			'delivery_ids': self.avl_delivery_ids.ids,
		})

		return {
			'name': 'Create RMA',
			'type': 'ir.actions.act_window',
			'res_model': 'lot.repair.order.wizard',
			'view_mode': 'form',
			'res_id': wizard.id,
			'target': 'new',
			'context': {
				'default_stock_lot_id': self.id,
				'default_action_type': 'rma',
				'default_delivery_ids': self.avl_delivery_ids.ids,
			}
		}

	def button_view_repair(self):
		check_ids = self.env['repair.order'].search([('stock_lot_id', '=', self.id)])
		return {
			'name': _('Repair'),
			'binding_view_types': 'form',
			'view_mode': 'list,form',
			'res_model': 'repair.order',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', check_ids.ids)],
		}

	def button_view_rma(self):
		check_ids = self.env['stock.picking'].search([('stock_lot_id', '=', self.id)])
		return {
			'name': _('RMA'),
			'binding_view_types': 'form',
			'view_mode': 'list,form',
			'res_model': 'stock.picking',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', check_ids.ids)],
		}