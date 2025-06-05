from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date
from collections import defaultdict


class RepairActionWizard(models.TransientModel):
	_name = 'repair.action.wizard'
	_description = "Repair Action Wizard"
	_inherit = ['mail.thread', 'mail.activity.mixin']


	default_location_id = fields.Many2one('stock.location', 'Default Location', domain=[("usage", "=", "internal")])
	line_ids = fields.One2many('repair.action.line.wizard', 'repair_action_id', string="Products")
	replace_line_ids = fields.One2many('replace.action.line.wizard', 'replace_action_id', string="Replace Products")
	action_type = fields.Selection(
		[
			('replace', 'Replace'),
			('refund', 'Refund'),
			('return_to_customer', 'Return to Customer'),
			('rma', 'RMA')
		],
		string="Action Type")
	order_id = fields.Many2one('sale.order', string="Order")

	def action_rma(self):
		stock_picking_model = self.env['stock.picking']
		stock_move_line_model = self.env['stock.move.line']
		rma_location = self.env['stock.warehouse'].search(
			[('company_id', '=', self.env.company.id)], limit=1).rma_location

		if not rma_location:
			raise ValidationError(_("You need to fill RMA Location in Warehouse"))
		active_id = self.env.context.get('active_id')
		sale = self.env['sale.order'].browse(active_id)

		so_picking_id = stock_picking_model.search(
			[('sale_id', '=', sale.id)], limit=1)

		delivery = sale.picking_ids.filtered(
			lambda p: p.picking_type_id.code == 'outgoing' and p.state == 'done')

		tracked_products = delivery.mapped('move_ids_without_package').mapped('product_id').filtered(
			lambda p: p.tracking != 'none')

		lot_lines = delivery.mapped('move_line_ids').filtered(
			lambda ml: ml.product_id in tracked_products and ml.lot_id)
		lots = lot_lines.mapped('lot_id')

		expired_lots = lots.filtered(
			lambda l: l.expiration_date and l.expiration_date.date() <= date.today())

		valid_lots = lots.filtered(
			lambda l: l.expiration_date and l.expiration_date.date() >= date.today())

		valid_products = valid_lots.mapped('product_id')

		picking_type_in = self.env['stock.picking.type'].search(
			[('code', '=', 'incoming')], limit=1)

		move_lines_data = {}
		for ml in self.line_ids:
			key = (ml.product_id.id, ml.lot_id.id)
			move_lines_data[key] = move_lines_data.get(key, 0.0) + ml.quantity

		picking_vals = {
			'sale_id': sale.id,
			'origin': sale.name,
			'partner_id': sale.partner_id.id,
			'location_id': delivery.location_dest_id.id,
			'location_dest_id': rma_location.id,
			'picking_type_id': picking_type_in.id,
			'group_id': sale.procurement_group_id.id,
		}
		in_order = stock_picking_model.create(picking_vals)

		product_qty_map = defaultdict(float)
		for (product_id, lot_id), qty in move_lines_data.items():
			product_qty_map[product_id] += qty

		moves = self.env['stock.move']
		for line in self.line_ids:
			if line.product_id.id not in moves.mapped('product_id').ids:
				moves |= self.env['stock.move'].create({
					'name': line.product_id.name,
					'product_id': line.product_id.id,
					'product_uom_qty': line.quantity	,
					'product_uom': line.sale_line_id.product_uom.id,
					'location_id': so_picking_id.location_dest_id.id,
					'location_dest_id': rma_location.id,
					'picking_id': in_order.id,
					'origin_returned_move_id': line.move_id.id,
					'sale_line_id': line.sale_line_id.id,
					'to_refund': True
				})
			find_move = moves.filtered(lambda x: x.product_id == line.product_id)
			print(find_move)
			move_line = self.env['stock.move.line'].create({
				'move_id': find_move.id,
				'product_id': line.product_id.id,
				'product_uom_id': line.product_id.uom_id.id,
				'picking_id': find_move.picking_id.id, 
				'quantity': line.quantity,
				'location_id': find_move.location_id.id,
				'location_dest_id': find_move.location_dest_id.id,
				'lot_name': line.lot_id.name,
				'lot_id': line.lot_id.id,
			})
			print(move_line)

		if sale.procurement_group_id:
			in_order.write({'group_id': sale.procurement_group_id.id})
		in_order.action_confirm()
		in_order.button_validate() 

		msg_body = _('Tus productos están en garantía y se enviaron correctamente al RMA : %s') % in_order.name
		sale.message_post(body=msg_body)
		sale.repair_status = 'rma'

		return True

	def action_return_to_customer(self):
		active_id = self.env.context.get('active_id')
		sale = self.env['sale.order'].browse(active_id)
		if not sale:
			raise ValidationError(_("No active sale order found in context."))

		stock_picking_model = self.env['stock.picking']

		so_picking_id = stock_picking_model.search(
			[('sale_id', '=', sale.id)], limit=1)

		if not so_picking_id:
			raise ValidationError(_("No related picking found for sale order."))

		picking_type_in = self.env['stock.picking.type'].search(
			[('code', '=', 'incoming')], limit=1)

		picking_type_out = self.env['stock.picking.type'].search(
			[('code', '=', 'outgoing')], limit=1)

		move_lines_data = {}
		for ml in self.line_ids:
			key = (ml.product_id.id, ml.lot_id.id)
			move_lines_data[key] = move_lines_data.get(key, 0.0) + ml.quantity

		# --- Incoming Picking (In Order) ---
		if picking_type_in:
			picking_in_vals = {
				'sale_id': sale.id,
				'origin': sale.name,
				'partner_id': sale.partner_id.id,
				'location_id': so_picking_id.location_dest_id.id,
				'location_dest_id': so_picking_id.location_id.id,
				'picking_type_id': picking_type_in.id,
				'group_id': sale.procurement_group_id.id,
			}
			picking_in = stock_picking_model.create(picking_in_vals)

		product_qty_map = defaultdict(float)
		for (product_id, lot_id), qty in move_lines_data.items():
			product_qty_map[product_id] += qty

		moves = self.env['stock.move']
		for line in self.line_ids:
			if line.product_id.id not in moves.mapped('product_id').ids:
				moves |= self.env['stock.move'].create({
					'name': line.product_id.name,
					'product_id': line.product_id.id,
					'product_uom_qty': line.quantity,
					'product_uom': line.sale_line_id.product_uom.id,
					'location_id': so_picking_id.location_dest_id.id,
					'location_dest_id': so_picking_id.location_id.id,
					'picking_id': picking_in.id,
					'origin_returned_move_id': line.move_id.id,
					'sale_line_id': line.sale_line_id.id,
					'to_refund': True
				})
			find_move = moves.filtered(lambda x: x.product_id == line.product_id)
			print(find_move)
			move_line = self.env['stock.move.line'].create({
				'move_id': find_move.id,
				'product_id': line.product_id.id,
				'product_uom_id': line.product_id.uom_id.id,
				'picking_id': find_move.picking_id.id, 
				'quantity': line.quantity,
				'location_id': find_move.location_id.id,
				'location_dest_id': find_move.location_dest_id.id,
				'lot_name': line.lot_id.name,
				'lot_id': line.lot_id.id,
			})
			print(move_line)

			if sale.procurement_group_id:
				picking_in.write({'group_id': sale.procurement_group_id.id})
			picking_in.action_confirm()
			picking_in.button_validate()

		msg_body_in = _('Orden devuelta con éxito a la persona cliente, IN Picking : %s') % picking_in.name
		sale.message_post(body=msg_body_in)

		# --- Outgoing Picking (Out Order) ---
		if picking_type_out:
			picking_out_vals = {
				'sale_id': sale.id,
				'origin': sale.name,
				'partner_id': sale.partner_id.id,
				'location_id': so_picking_id.location_id.id,
				'location_dest_id': so_picking_id.location_dest_id.id,
				'picking_type_id': picking_type_out.id,
				'group_id': sale.procurement_group_id.id,
			}
			picking_out = stock_picking_model.create(picking_out_vals)

		moves = self.env['stock.move']
		for line in self.line_ids:
			if line.product_id.id not in moves.mapped('product_id').ids:
				moves |= self.env['stock.move'].create({
					'name': line.product_id.name,
					'product_id': line.product_id.id,
					'product_uom_qty': line.quantity,
					'product_uom': line.sale_line_id.product_uom.id,
					'location_id': so_picking_id.location_id.id,
					'location_dest_id': so_picking_id.location_dest_id.id,
					'picking_id': picking_out.id,
					'origin_returned_move_id': line.move_id.id,
					'sale_line_id': line.sale_line_id.id,
					'to_refund': True
				})
			find_move = moves.filtered(lambda x: x.product_id == line.product_id)
			print(find_move)
			move_line = self.env['stock.move.line'].create({
				'move_id': find_move.id,
				'product_id': line.product_id.id,
				'product_uom_id': line.product_id.uom_id.id,
				'picking_id': find_move.picking_id.id, 
				'quantity': line.quantity,
				'location_id': find_move.location_dest_id.id,
				'location_dest_id': find_move.location_id.id,
				'lot_name': line.lot_id.name,
				'lot_id': line.lot_id.id,
			})
			print(move_line)

			if sale.procurement_group_id:
				picking_out.write({'group_id': sale.procurement_group_id.id})
			picking_out.action_confirm()
			picking_out.button_validate()

		msg_body_out = _('Orden devuelta con éxito a la persona cliente, OUT Picking : %s') % picking_out.name
		sale.message_post(body=msg_body_out)
		sale.repair_status = 'return_to_customer'

		return True

	def _prepare_default_reversal(self, move):
		reverse_date = date.today()
		active_id = self.env.context.get('active_id')
		sale = self.env['sale.order'].browse(active_id)
		account_data = self.env['account.move'].search([
			('invoice_origin', '=', sale.name),
			('move_type', '=', 'out_invoice')
		])
		mixed_payment_term = move.invoice_payment_term_id.id if move.invoice_payment_term_id.early_pay_discount_computation == 'mixed' else None
		return {
			'ref': _('Reversal of: %(move_name)s, (Refund)', move_name=move.name),
			'date': reverse_date,
			'invoice_date_due': reverse_date,
			'invoice_date': move.is_invoice(include_receipts=True) and (reverse_date or move.date) or False,
			'journal_id': account_data.journal_id.id,
			'invoice_payment_term_id': mixed_payment_term,
			'invoice_user_id': move.invoice_user_id.id,
			'auto_post': 'at_date' if reverse_date > fields.Date.context_today(self) else 'no',
		}

	def reverse_moves(self, is_modify=False):
		self.ensure_one()
		active_id = self.env.context.get('active_id')
		sale = self.env['sale.order'].browse(active_id)
		moves = sale.invoice_ids.filtered(
			lambda p: p.move_type == 'out_invoice' and p.state == 'posted')
		# moves = sale.invoice_ids.search(
		# 	[('move_type', '=', 'out_invoice'),('payment_state','=', 'paid')], limit=1)
		
		print('moves>>>>>>>>>>>>',moves.name)

		default_values_list = []
		for move in moves:
			default_values_list.append(self._prepare_default_reversal(move))

		batches = [
			[self.env['account.move'], [], True],
			[self.env['account.move'], [], False],
		]
		for move, default_vals in zip(moves, default_values_list):
			is_auto_post = default_vals.get('auto_post') != 'no'
			is_cancel_needed = not is_auto_post and is_modify
			batch_index = 0 if is_cancel_needed else 1
			batches[batch_index][0] |= move
			batches[batch_index][1].append(default_vals)

		moves_to_redirect = self.env['account.move']
		for moves, default_values_list, is_cancel_needed in batches:
			new_moves = moves._reverse_moves(default_values_list, cancel=is_cancel_needed)
			moves._message_log_batch(
				bodies={move.id: _('This entry has been %s', reverse._get_html_link(title=_("reversed"))) for move, reverse in zip(moves, new_moves)}
			)

			if is_modify:
				reverse_date = date.today()
				moves_vals_list = []
				for move in moves.with_context(include_business_fields=True):
					moves_vals_list.append(move.copy_data({'date': reverse_date})[0])
				new_moves = self.env['account.move'].create(moves_vals_list)

			moves_to_redirect |= new_moves

		action = {
			'name': _('Reverse Moves'),
			'type': 'ir.actions.act_window',
			'res_model': 'account.move',
		}
		if len(moves_to_redirect) == 1:
			action.update({
				'view_mode': 'form',
				'res_id': moves_to_redirect.id,
				'context': {'default_move_type':  moves_to_redirect.move_type},
			})
		else:
			action.update({
				'view_mode': 'tree,form',
				'domain': [('id', 'in', moves_to_redirect.ids)],
			})
			if len(set(moves_to_redirect.mapped('move_type'))) == 1:
				action['context'] = {'default_move_type':  moves_to_redirect.mapped('move_type').pop()}

		if moves_to_redirect:
			for move in moves_to_redirect:
				move.action_post()
				sale.message_post(body=_('Nota de crédito del cliente creada : %s') % move.name)
			sale.repair_status = 'refund'
		return action


	def action_replace(self):

		if not self.default_location_id:
			raise ValidationError(_("Select Return Location for further process."))

		active_id = self.env.context.get('active_id')
		sale = self.env['sale.order'].browse(active_id)
		if not sale:
			raise ValidationError(_("No active sale order found in context."))

		stock_picking_model = self.env['stock.picking']

		so_picking_id = stock_picking_model.search(
			[('sale_id', '=', sale.id)], limit=1)

		if not so_picking_id:
			raise ValidationError(_("No related picking found for sale order."))

		picking_type_in = self.env['stock.picking.type'].search(
			[('code', '=', 'incoming')], limit=1)

		picking_type_out = self.env['stock.picking.type'].search(
			[('code', '=', 'outgoing')], limit=1)

		move_lines_data = {}
		for ml in self.line_ids:
			key = (ml.product_id.id, ml.lot_id.id)
			move_lines_data[key] = move_lines_data.get(key, 0.0) + ml.quantity

		# --- Incoming Picking (In Order) ---
		if picking_type_in:
			picking_in_vals = {
				'sale_id': sale.id,
				'origin': sale.name,
				'partner_id': sale.partner_id.id,
				'location_id': so_picking_id.location_dest_id.id,
				'location_dest_id': self.default_location_id.id,
				'picking_type_id': picking_type_in.id,
				'group_id': sale.procurement_group_id.id,
			}
			picking_in = stock_picking_model.create(picking_in_vals)

		product_qty_map = defaultdict(float)
		for (product_id, lot_id), qty in move_lines_data.items():
			product_qty_map[product_id] += qty

		moves = self.env['stock.move']
		for line in self.line_ids:
			if line.product_id.id not in moves.mapped('product_id').ids:
				moves |= self.env['stock.move'].create({
					'name': line.product_id.name,
					'product_id': line.product_id.id,
					'product_uom_qty': line.quantity,
					'product_uom': line.sale_line_id.product_uom.id,
					'location_id': so_picking_id.location_dest_id.id,
					'location_dest_id': self.default_location_id.id,
					'picking_id': picking_in.id,
					'origin_returned_move_id': line.move_id.id,
					'sale_line_id': line.sale_line_id.id,
					'to_refund': True
				})
			find_move = moves.filtered(lambda x: x.product_id == line.product_id)
			print(find_move)
			move_line = self.env['stock.move.line'].create({
				'move_id': find_move.id,
				'product_id': line.product_id.id,
				'product_uom_id': line.product_id.uom_id.id,
				'picking_id': find_move.picking_id.id, 
				'quantity': line.quantity,
				'location_id': find_move.location_id.id,
				'location_dest_id': self.default_location_id.id,
				'lot_name': line.lot_id.name,
				'lot_id': line.lot_id.id,
			})
			print(move_line)

			if sale.procurement_group_id:
				picking_in.write({'group_id': sale.procurement_group_id.id})
			picking_in.action_confirm()
			picking_in.button_validate()

		msg_body_in = _('Orden reemplazada con éxito, IN Picking : %s') % picking_in.name
		sale.message_post(body=msg_body_in)

		# move_lines_data_out = {}
		# for ml in self.line_ids:
		# 	key = (ml.product_id.id, ml.lot_id.id)
		# 	move_lines_data_out[key] = move_lines_data_out.get(key, 0.0) + ml.quantity

		if not self.replace_line_ids:
			raise ValidationError(_("You Don't selected Products to Replace."))

		for line in self.replace_line_ids:
			line_date = self.order_id.order_line.create({
				'order_id': sale.id,
				'product_id': line.product_id.id,
				'product_uom_qty': line.quantity,
			})
			print('line_date******************',line_date)


		# # --- Outgoing Picking (Out Order) ---
		# if picking_type_out:
		# 	picking_out_vals = {
		# 		'sale_id': sale.id,
		# 		'origin': sale.name,
		# 		'partner_id': sale.partner_id.id,
		# 		'location_id': self.default_location_id.id,
		# 		'location_dest_id': so_picking_id.location_dest_id.id,
		# 		'picking_type_id': picking_type_out.id,
		# 		'group_id': sale.procurement_group_id.id,
		# 	}
		# 	picking_out = stock_picking_model.create(picking_out_vals)

		# product_qty_map = defaultdict(float)
		# for (product_id, lot_id), qty in move_lines_data_out.items():
		# 	product_qty_map[product_id] += qty

		# moves = self.env['stock.move']
		# for line in self.line_ids:
		# 	if line.product_id.id not in moves.mapped('product_id').ids:
		# 		moves |= self.env['stock.move'].create({
		# 			'name': line.product_id.name,
		# 			'product_id': line.product_id.id,
		# 			'product_uom_qty': line.quantity,
		# 			'product_uom': line.sale_line_id.product_uom.id,
		# 			'location_id': so_picking_id.location_dest_id.id,
		# 			'location_dest_id': so_picking_id.location_dest_id.id,
		# 			'picking_id': picking_out.id,
		# 			'origin_returned_move_id': line.move_id.id,
		# 			'sale_line_id': line.sale_line_id.id,
		# 			'to_refund': True
		# 		})
		# 	find_move = moves.filtered(lambda x: x.product_id == line.product_id)
		# 	print(find_move)
		# 	move_line = self.env['stock.move.line'].create({
		# 		'move_id': find_move.id,
		# 		'product_id': line.product_id.id,
		# 		'product_uom_id': line.product_id.uom_id.id,
		# 		'picking_id': find_move.picking_id.id, 
		# 		'quantity': line.quantity,
		# 		'location_id': find_move.location_id.id,
		# 		'location_dest_id': so_picking_id.location_dest_id.id,
		# 		'lot_name': line.lot_id.name,
		# 		'lot_id': line.lot_id.id,
		# 	})
		# 	print(move_line)
		
		# 	if sale.procurement_group_id:
		# 		picking_out.write({'group_id': sale.procurement_group_id.id})
		# 	picking_out.action_confirm()
		# 	picking_out.button_validate()

		# 	msg_body_out = _('Orden reemplazada con éxito, OUT Picking : %s') % picking_out.name
		# 	sale.message_post(body=msg_body_out)
			sale.repair_status = 'replace'
		
		return True

	def action_return_order(self):
		self.reverse_moves()
		"""In Order"""
		stock_picking_model = self.env['stock.picking']
		active_id = self.env.context.get('active_id')
		sale = self.env['sale.order'].browse(active_id)

		if not self.default_location_id:
			raise ValidationError(_("Select Return Location for further process."))

		# --- Incoming Picking (In Order) ---
		incoming = stock_picking_model.search(
			[('sale_id', '=', sale.id)],
			limit=1
		)
		if not incoming:
			raise ValueError(_("No matching incoming picking found for the sale order."))
		incoming.ensure_one()

		picking_type_in = self.env['stock.picking.type'].search(
			[('code', '=', 'incoming')], limit=1
		)
		if not picking_type_in or not picking_type_in.sequence_id:
			raise ValueError(_("Incoming picking type or sequence is not properly configured."))

		move_lines_data = {}
		for ml in self.line_ids:
			key = (ml.product_id.id, ml.lot_id.id)
			move_lines_data[key] = move_lines_data.get(key, 0.0) + ml.quantity

		return_picking_vals = {
			'sale_id': sale.id,
			'origin': sale.name,
			'partner_id': sale.partner_id.id,
			'location_id': incoming.location_dest_id.id,
			'location_dest_id': self.default_location_id.id,
			'picking_type_id': picking_type_in.id,
		}
		return_picking = stock_picking_model.create(return_picking_vals)

		product_qty_map = defaultdict(float)
		for (product_id, lot_id), qty in move_lines_data.items():
			product_qty_map[product_id] += qty

		moves = self.env['stock.move']
		for line in self.line_ids:
			if line.product_id.id not in moves.mapped('product_id').ids:
				moves |= self.env['stock.move'].create({
					'name': line.product_id.name,
					'product_id': line.product_id.id,
					'product_uom_qty': line.quantity,
					'product_uom': line.sale_line_id.product_uom.id,
					'location_id': incoming.location_dest_id.id,
					'location_dest_id': self.default_location_id.id,
					'picking_id': return_picking.id,
					'origin_returned_move_id': line.move_id.id,
					'sale_line_id': line.sale_line_id.id,
					'to_refund': True
				})
			find_move = moves.filtered(lambda x: x.product_id == line.product_id)
			print(find_move)
			move_line = self.env['stock.move.line'].create({
				'move_id': find_move.id,
				'product_id': line.product_id.id,
				'product_uom_id': line.product_id.uom_id.id,
				'picking_id': find_move.picking_id.id, 
				'quantity': line.quantity,
				'location_id': find_move.location_id.id,
				'location_dest_id': self.default_location_id.id,
				'lot_name': line.lot_id.name,
				'lot_id': line.lot_id.id,
			})
			print(move_line)
		return_picking.action_confirm()
		return_picking.button_validate()

		# self.env['mail.message'].sudo().create({
		# 	"message_type": 'comment',
		# 	'model': 'sale.order',
		# 	'res_id': sale.id,
		# 	"body": _('Pedido devuelto con éxito, IN Order : %s') % return_picking.name
		# })
		msg_body = _('Pedido devuelto con éxito, IN Order : %s') % return_picking.name
		sale.message_post(body=msg_body)
		sale.repair_status = 'refund'	

		return True


class RepairActionLineWizard(models.TransientModel):
	_name = 'repair.action.line.wizard'
	_description = "Repair Action Line Wizard"

	repair_action_id = fields.Many2one(
		'repair.action.wizard',
		string="Repair Action",
	)
	product_id = fields.Many2one('product.product', string="Product")
	quantity = fields.Float(string="Quantity")
	lot_id = fields.Many2one('stock.lot', string="Lot/Serial Number")
	sale_line_id = fields.Many2one("sale.order.line", "Line")
	move_id = fields.Many2one("stock.move", "Move")


class ReplaceActionLineWizard(models.TransientModel):
	_name = 'replace.action.line.wizard'
	_description = "Replace Action Line Wizard"

	replace_action_id = fields.Many2one(
		'repair.action.wizard',
		string="Replace Action",
	)
	product_id = fields.Many2one('product.product', string="Product")
	quantity = fields.Float(string="Quantity")
	lot_id = fields.Many2one('stock.lot', string="Lot/Serial Number")