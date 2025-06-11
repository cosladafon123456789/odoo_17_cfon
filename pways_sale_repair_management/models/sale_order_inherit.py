# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, SUPERUSER_ID
from collections import defaultdict
from odoo.exceptions import ValidationError
from datetime import date
from datetime import timedelta
from collections import defaultdict


class SaleOrder(models.Model):
	_inherit = "sale.order"

	repair_check_count = fields.Integer(string="Count", compute="_compute_repair_check_count")
	replace_count = fields.Integer(string="Replace Count", compute="_compute_replace_count")
	delivery_check = fields.Boolean("Check Delivery", compute='_compute_delivery_check')
	delivery_done = fields.Boolean('Delivery Done', default=False)
	is_warranty = fields.Boolean('Warranty')
	repair_status = fields.Selection(
	[
		('received', 'Recibido'),
		('repair', 'Reparación'),
		('replace', 'Reemplazar'),
		('refund', 'Reembolsar'),
		('return_to_customer', 'Devolver Al Cliente'),
		('rma', 'RMA')
	],
	string='Estado De Reparacion')


	def button_recieved(self):
		self.repair_status = 'received'
		self.delivery_done = True
		msg_body = _('El cliente ha recibido los productos.')
		self.message_post(body=msg_body)
		return True

	def button_replace(self):
		self.ensure_one()

		repair_lines = self.order_line.filtered(lambda l: l.create_repair_order)
		if not repair_lines:
			raise ValidationError(_("No lines are selected to create replace order."))

		wizard = self.env['repair.action.wizard'].create({
			'action_type': 'replace',
			'order_id': self.id,
		})

		deliveries = self.picking_ids.filtered(
			lambda p: p.picking_type_id.code == 'outgoing' and p.state == 'done')

		lot_lines = deliveries.mapped('move_line_ids').filtered(
			lambda ml: ml.product_id.tracking != 'none' and ml.lot_id)

		product_lot_qty_map = defaultdict(float)
		move_lot_id =  defaultdict(float)
		for ml in lot_lines:
			product_lot_qty_map[(ml.product_id.id, ml.lot_id.id, ml.move_id.sale_line_id.id)] += ml.quantity
			move_lot_id[(ml.product_id.id, ml.lot_id.id, ml.move_id.sale_line_id.id)] = ml.move_id.id
		lot_wise_dict = {}
		for line in self.order_line:
			if line.qty_delivered_method == 'stock_move':
				outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
				out_move_lines = outgoing_moves.mapped('move_line_ids')
				in_move_lines = incoming_moves.mapped('move_line_ids')
				for move_line in out_move_lines:
					if move_line.move_id.state == 'done' and move_line.lot_id:
						lot = move_line.lot_id
						lot_wise_dict[lot.id] = lot_wise_dict.get(lot.id, 0.0) + move_line.quantity
				for move_line in in_move_lines:
					if move_line.move_id.state == 'done' and move_line.lot_id:
						lot = move_line.lot_id
						if lot_wise_dict.get(lot.id, False):
							lot_wise_dict[lot.id] -= move_line.quantity
		created = False
		for (product_id, lot_id, line_id), qty in product_lot_qty_map.items():
			move_id = move_lot_id[(product_id, lot_id, line_id)]
			quantity = lot_wise_dict[lot_id]
			if quantity > 0:
				repair_action_line = self.env['repair.action.line.wizard'].create({
					'repair_action_id': wizard.id,
					'product_id': product_id,
					'lot_id': lot_id,
					'sale_line_id': line_id,
					'move_id': move_id, 
					'quantity': quantity,
				})
				created = True
		if not created:
			raise ValidationError(_("You don't have products to create Replace"))

		return {
			'name': 'All Action Order',
			'type': 'ir.actions.act_window',
			'res_model': 'repair.action.wizard',
			'view_mode': 'form',
			'res_id': wizard.id,
			'target': 'new',
			'context': {
				'default_order_id': self.id,
				'default_action_type': 'replace',
			}
		}

	def button_refund(self):
		self.ensure_one()

		repair_lines = self.order_line.filtered(lambda l: l.create_repair_order)
		if not repair_lines:
			raise ValidationError(_("No lines are selected to create Refund."))
		
		payment = self.invoice_ids.filtered(
			lambda p: p.move_type == 'out_invoice' and p.state == 'posted')
		if not payment:
			raise ValidationError(_("You must create the Invoice and Validate it before creating a refund."))

		wizard = self.env['repair.action.wizard'].create({
			'action_type': 'refund',
			'order_id': self.id,
			})

		deliveries = self.picking_ids.filtered(
			lambda p: p.picking_type_id.code == 'outgoing' and p.state == 'done')

		lot_lines = deliveries.mapped('move_line_ids').filtered(
			lambda ml: ml.product_id.tracking != 'none' and ml.lot_id)

		product_lot_qty_map = defaultdict(float)
		move_lot_id =  defaultdict(float)
		for ml in lot_lines:
			product_lot_qty_map[(ml.product_id.id, ml.lot_id.id, ml.move_id.sale_line_id.id)] += ml.quantity
			move_lot_id[(ml.product_id.id, ml.lot_id.id, ml.move_id.sale_line_id.id)] = ml.move_id.id
		lot_wise_dict = {}
		for line in self.order_line:
			if line.qty_delivered_method == 'stock_move':
				outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
				out_move_lines = outgoing_moves.mapped('move_line_ids')
				in_move_lines = incoming_moves.mapped('move_line_ids')
				for move_line in out_move_lines:
					if move_line.move_id.state == 'done' and move_line.lot_id:
						lot = move_line.lot_id
						lot_wise_dict[lot.id] = lot_wise_dict.get(lot.id, 0.0) + move_line.quantity
				for move_line in in_move_lines:
					if move_line.move_id.state == 'done' and move_line.lot_id:
						lot = move_line.lot_id
						if lot_wise_dict.get(lot.id, False):
							lot_wise_dict[lot.id] -= move_line.quantity
		created = False
		for (product_id, lot_id, line_id), qty in product_lot_qty_map.items():
			move_id = move_lot_id[(product_id, lot_id, line_id)]
			quantity = lot_wise_dict[lot_id]
			if quantity > 0:
				repair_action_line = self.env['repair.action.line.wizard'].create({
					'repair_action_id': wizard.id,
					'product_id': product_id,
					'lot_id': lot_id,
					'sale_line_id': line_id,
					'move_id': move_id, 
					'quantity': quantity,
				})
				created = True
		if not created:
			raise ValidationError(_("You don't have products to create Refund."))

		return {
			'name': 'All Action Order',
			'type': 'ir.actions.act_window',
			'res_model': 'repair.action.wizard',
			'view_mode': 'form',
			'res_id': wizard.id,
			'target': 'new',
			'context': {
				'default_order_id': self.id,
				'default_action_type': 'refund',
			}
		}		

	def button_return_to_customer(self):
		self.ensure_one()

		repair_lines = self.order_line.filtered(lambda l: l.create_repair_order)
		if not repair_lines:
			raise ValidationError(_("No lines are selected to create Return order to Customer."))

		wizard = self.env['repair.action.wizard'].create({
			'action_type': 'return_to_customer',
			'order_id': self.id,
		})

		deliveries = self.picking_ids.filtered(
			lambda p: p.picking_type_id.code == 'outgoing' and p.state == 'done')

		lot_lines = deliveries.mapped('move_line_ids').filtered(
			lambda ml: ml.product_id.tracking != 'none' and ml.lot_id)

		product_lot_qty_map = defaultdict(float)
		move_lot_id =  defaultdict(float)
		for ml in lot_lines:
			product_lot_qty_map[(ml.product_id.id, ml.lot_id.id, ml.move_id.sale_line_id.id)] += ml.quantity
			move_lot_id[(ml.product_id.id, ml.lot_id.id, ml.move_id.sale_line_id.id)] = ml.move_id.id
		lot_wise_dict = {}
		for line in self.order_line:
			if line.qty_delivered_method == 'stock_move':
				outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
				out_move_lines = outgoing_moves.mapped('move_line_ids')
				in_move_lines = incoming_moves.mapped('move_line_ids')
				for move_line in out_move_lines:
					if move_line.move_id.state == 'done' and move_line.lot_id:
						lot = move_line.lot_id
						lot_wise_dict[lot.id] = lot_wise_dict.get(lot.id, 0.0) + move_line.quantity
				for move_line in in_move_lines:
					if move_line.move_id.state == 'done' and move_line.lot_id:
						lot = move_line.lot_id
						if lot_wise_dict.get(lot.id, False):
							lot_wise_dict[lot.id] -= move_line.quantity
		created = False
		for (product_id, lot_id, line_id), qty in product_lot_qty_map.items():
			move_id = move_lot_id[(product_id, lot_id, line_id)]
			quantity = lot_wise_dict[lot_id]
			if quantity > 0:
				repair_action_line = self.env['repair.action.line.wizard'].create({
					'repair_action_id': wizard.id,
					'product_id': product_id,
					'lot_id': lot_id,
					'sale_line_id': line_id,
					'move_id': move_id, 
					'quantity': quantity,
				})
				created = True
		if not created:
			raise ValidationError(_("You don't have products to Return."))

		return {
			'name': 'All Action Order',
			'type': 'ir.actions.act_window',
			'res_model': 'repair.action.wizard',
			'view_mode': 'form',
			'res_id': wizard.id,
			'target': 'new',
			'context': {
				'default_order_id': self.id,
				'default_action_type': 'return_to_customer',
			}
		}

	def button_rma(self):
		self.ensure_one()

		repair_lines = self.order_line.filtered(lambda l: l.create_repair_order)
		if not repair_lines:
			raise ValidationError(_("No lines are selected to create RMA."))

		wizard = self.env['repair.action.wizard'].create({
			'action_type': 'rma',
			'order_id': self.id,
		})

		deliveries = self.picking_ids.filtered(
			lambda p: p.picking_type_id.code == 'outgoing' and p.state == 'done')

		tracked_lot_lines = deliveries.mapped('move_line_ids').filtered(
			lambda ml: ml.product_id.tracking != 'none' and ml.lot_id and ml.move_id.sale_line_id.id in repair_lines.ids)

		if not tracked_lot_lines:
			raise ValidationError(_("You don't have products to create RMA."))

		warranty_lines = tracked_lot_lines.filtered(
			lambda ml: ml.lot_id.expiration_date and ml.lot_id.expiration_date.date() >= date.today())

		if not warranty_lines:
			raise ValidationError(_("You don't have products under warranty to create RMA."))

		product_lot_qty_map = defaultdict(float)
		move_lot_id =  defaultdict(float)
		for ml in warranty_lines:
			product_lot_qty_map[(ml.product_id.id, ml.lot_id.id, ml.move_id.sale_line_id.id)] += ml.quantity
			move_lot_id[(ml.product_id.id, ml.lot_id.id, ml.move_id.sale_line_id.id)] = ml.move_id.id
		lot_wise_dict = {}
		for line in self.order_line:
			if line.qty_delivered_method == 'stock_move':
				outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
				out_move_lines = outgoing_moves.mapped('move_line_ids')
				in_move_lines = incoming_moves.mapped('move_line_ids')
				for move_line in out_move_lines:
					if move_line.move_id.state == 'done' and move_line.lot_id:
						lot = move_line.lot_id
						lot_wise_dict[lot.id] = lot_wise_dict.get(lot.id, 0.0) + move_line.quantity
				for move_line in in_move_lines:
					if move_line.move_id.state == 'done' and move_line.lot_id:
						lot = move_line.lot_id
						if lot_wise_dict.get(lot.id, False):
							lot_wise_dict[lot.id] -= move_line.quantity
		created = False
		for (product_id, lot_id, line_id), qty in product_lot_qty_map.items():
			move_id = move_lot_id[(product_id, lot_id, line_id)]
			quantity = lot_wise_dict[lot_id]
			if quantity > 0:
				repair_action_line = self.env['repair.action.line.wizard'].create({
					'repair_action_id': wizard.id,
					'product_id': product_id,
					'lot_id': lot_id,
					'sale_line_id': line_id,
					'move_id': move_id, 
					'quantity': quantity,
				})
				created = True
		if not created:
			raise ValidationError(_("You don't have products to create RMA."))

		return {
			'name': 'All Action Order',
			'type': 'ir.actions.act_window',
			'res_model': 'repair.action.wizard',
			'view_mode': 'form',
			'res_id': wizard.id,
			'target': 'new',
			'context': {
				'default_order_id': self.id,
				'default_action_type': 'rma',
			}
		}

	def _compute_delivery_check(self):
		for rec in self:
			delivery_check = False

			deliveries = self.picking_ids.filtered(
				lambda p: p.picking_type_id.code == 'outgoing')

			if deliveries and all(p.state == 'done' for p in deliveries):
				delivery_check = True

			rec.delivery_check = delivery_check

	def button_create_repair_order(self):
		has_create_repair_order = any(line.create_repair_order for line in self.order_line)
		if not has_create_repair_order:
			raise ValidationError(_("No lines are selected to create repair order."))

		action = self.env["ir.actions.actions"]._for_xml_id("pways_sale_repair_management.create_repair_order_action")
		return action

	def button_view_rapir_orders(self):
		activities = self.env['repair.order'].sudo().search([('sale_order_id', '=', self.id)])
		action = self.env["ir.actions.actions"]._for_xml_id("repair.action_repair_order_tree")
		action['domain'] = [('id', 'in', activities.ids)]
		return action

	def _compute_repair_check_count(self):
		count_of_repair = self.env['repair.order'].search_count([('sale_order_id', '=', self.id)])
		self.repair_check_count = count_of_repair

	def button_view_replace_orders(self):
		activities = self.env['stock.picking'].sudo().search([('replace_id', '=', self.id)])
		action = self.env["ir.actions.actions"]._for_xml_id("stock.view_picking_form")
		action['domain'] = [('id', 'in', activities.ids)]
		return action

	def _compute_replace_count(self):
		count_of_repair = self.env['stock.picking'].search_count([('replace_id', '=', self.id)])
		self.replace_count = count_of_repair

class SaleOrderLine(models.Model):
	_inherit = "sale.order.line"

	create_repair_order = fields.Boolean(string="Repair" , copy=False)
