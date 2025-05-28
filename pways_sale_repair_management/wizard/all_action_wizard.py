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
		active_id = self.env.context.get('active_id')
		sale = self.env['sale.order'].browse(active_id)

		so_picking_id = stock_picking_model.search(
			[('sale_id', '=', sale.id)], limit=1)

		rma_location = self.env['stock.warehouse'].search(
			[('company_id', '=', self.env.company.id)], limit=1).rma_location

		if not rma_location:
			raise ValidationError(_("You need to fill RMA Location in Warehouse"))

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
		for ml in lot_lines:
			key = (ml.product_id.id, ml.lot_id.id)
			move_lines_data[key] = move_lines_data.get(key, 0.0) + ml.quantity

		picking_vals = {
			'sale_id': sale.id,
			'origin': sale.name,
			'partner_id': sale.partner_id.id,
			'location_id': so_picking_id.location_dest_id.id,
			'location_dest_id': rma_location.id,
			'picking_type_id': picking_type_in.id,
			'group_id': sale.procurement_group_id.id,
		}
		in_order = stock_picking_model.create(picking_vals)

		product_qty_map = defaultdict(float)
		for (product_id, lot_id), qty in move_lines_data.items():
			product_qty_map[product_id] += qty

		move_records = {}
		for line in sale.order_line.filtered('create_repair_order'):
			if line.product_id.id in product_qty_map and line.product_id in valid_products:
				move = self.env['stock.move'].create({
					'name': line.product_id.name,
					'product_id': line.product_id.id,
					'product_uom_qty': product_qty_map[line.product_id.id],
					'product_uom': line.product_uom.id,
					'location_id': so_picking_id.location_dest_id.id,
					'location_dest_id': rma_location.id,
					'picking_id': in_order.id,
					'sale_line_id': line.id,
				})
				move_records[line.product_id.id] = move

		for (product_id, lot_id), qty in move_lines_data.items():
			move = move_records.get(product_id)
			if move:
				self.env['stock.move.line'].create({
					'move_id': move.id,
					'product_id': product_id,
					'product_uom_id': move.product_uom.id,
					'quantity': qty,
					'location_id': move.location_id.id,
					'location_dest_id': move.location_dest_id.id,
					'lot_id': lot_id,
				})

		if sale.procurement_group_id:
			in_order.write({'group_id': sale.procurement_group_id.id})

		msg_body = _('Your Products are in Warranty, Sent Successfully to RMA %s') % in_order.name
		sale.message_post(body=msg_body)
		sale.repair_status = 'rma'

		return True



	def action_return_to_customer(self):
		active_id = self.env.context.get('active_id')
		sale = self.env['sale.order'].browse(active_id)
		if not sale:
			raise ValidationError("No active sale order found in context.")

		stock_picking_model = self.env['stock.picking']

		so_picking_id = stock_picking_model.search(
			[('sale_id', '=', sale.id)], limit=1)

		if not so_picking_id:
			raise ValidationError("No related picking found for sale order.")

		# Incoming picking type (return to customer in order)
		picking_type_in = self.env['stock.picking.type'].search(
			[('code', '=', 'incoming')], limit=1)

		# Outgoing picking type (return to customer out order)
		picking_type_out = self.env['stock.picking.type'].search(
			[('code', '=', 'outgoing')], limit=1)

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

			for line in sale.order_line.filtered('create_repair_order'):
				move_vals = {
					'picking_id': picking_in.id,
					'product_id': line.product_id.id,
					'product_uom_qty': line.product_uom_qty,
					'product_uom': line.product_uom.id,
					'location_id': so_picking_id.location_dest_id.id,
					'location_dest_id': so_picking_id.location_id.id,
					'name': line.product_id.display_name,
					'sale_line_id': line.id,
				}
				move = self.env['stock.move'].create(move_vals)

				# Find existing move lines in original picking with lot for this product
				orig_move_lines = so_picking_id.move_line_ids.filtered(
					lambda ml: ml.product_id == line.product_id and ml.lot_id)

				if orig_move_lines:
					for ml in orig_move_lines:
						self.env['stock.move.line'].create({
							'move_id': move.id,
							'product_id': ml.product_id.id,
							'product_uom_id': ml.product_uom_id.id,
							'location_id': so_picking_id.location_dest_id.id,
							'location_dest_id': so_picking_id.location_id.id,
							'lot_id': ml.lot_id.id,
							'quantity': ml.quantity,
						})
				else:
					self.env['stock.move.line'].create({
						'move_id': move.id,
						'product_id': line.product_id.id,
						'product_uom_id': line.product_uom.id,
						'location_id': so_picking_id.location_dest_id.id,
						'location_dest_id': so_picking_id.location_id.id,
						'quantity': line.product_uom_qty,
					})

			if sale.procurement_group_id:
				picking_in.write({'group_id': sale.procurement_group_id.id})

			msg_body_in = _('Order Successfully Returned to Customer IN Picking %s') % picking_in.name
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

			for line in sale.order_line.filtered('create_repair_order'):
				move_vals = {
					'picking_id': picking_out.id,
					'product_id': line.product_id.id,
					'product_uom_qty': line.product_uom_qty,
					'product_uom': line.product_uom.id,
					'location_id': so_picking_id.location_id.id,
					'location_dest_id': so_picking_id.location_dest_id.id,
					'name': line.product_id.display_name,
					'sale_line_id': line.id,
				}
				move = self.env['stock.move'].create(move_vals)

				orig_move_lines = so_picking_id.move_line_ids.filtered(
					lambda ml: ml.product_id == line.product_id and ml.lot_id)

				if orig_move_lines:
					for ml in orig_move_lines:
						self.env['stock.move.line'].create({
							'move_id': move.id,
							'product_id': ml.product_id.id,
							'product_uom_id': ml.product_uom_id.id,
							'location_id': so_picking_id.location_id.id,
							'location_dest_id': so_picking_id.location_dest_id.id,
							'lot_id': ml.lot_id.id,
							'quantity': ml.quantity,
						})
				else:
					self.env['stock.move.line'].create({
						'move_id': move.id,
						'product_id': line.product_id.id,
						'product_uom_id': line.product_uom.id,
						'location_id': so_picking_id.location_id.id,
						'location_dest_id': so_picking_id.location_dest_id.id,
						'quantity	': line.product_uom_qty,
					})

			if sale.procurement_group_id:
				picking_out.write({'group_id': sale.procurement_group_id.id})

			msg_body_out = _('Order Successfully Returned to Customer OUT Picking %s') % picking_out.name
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
		moves = sale.invoice_ids

		# Create default values.
		default_values_list = []
		for move in moves:
			default_values_list.append(self._prepare_default_reversal(move))

		batches = [
			[self.env['account.move'], [], True],   # Moves to be cancelled by the reverses.
			[self.env['account.move'], [], False],  # Others.
		]
		for move, default_vals in zip(moves, default_values_list):
			is_auto_post = default_vals.get('auto_post') != 'no'
			is_cancel_needed = not is_auto_post and is_modify
			batch_index = 0 if is_cancel_needed else 1
			batches[batch_index][0] |= move
			batches[batch_index][1].append(default_vals)

		# Handle reverse method.
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

		# Create action.
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

		sale.message_post(body=_('Customer Credit Note Created.'))
		sale.repair_status = 'refund'
		return action


	def action_replace(self):

		if not self.default_location_id:
			raise ValidationError(_("Select Return Location for further process."))

		active_id = self.env.context.get('active_id')
		sale = self.env['sale.order'].browse(active_id)
		if not sale:
			raise ValidationError("No active sale order found in context.")

		stock_picking_model = self.env['stock.picking']

		so_picking_id = stock_picking_model.search(
			[('sale_id', '=', sale.id)], limit=1)

		if not so_picking_id:
			raise ValidationError("No related picking found for sale order.")

		# Incoming picking type (return to customer in order)
		picking_type_in = self.env['stock.picking.type'].search(
			[('code', '=', 'incoming')], limit=1)

		# Outgoing picking type (return to customer out order)
		picking_type_out = self.env['stock.picking.type'].search(
			[('code', '=', 'outgoing')], limit=1)

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

			for line in sale.order_line.filtered('create_repair_order'):
				move_vals = {
					'picking_id': picking_in.id,
					'product_id': line.product_id.id,
					'product_uom_qty': line.product_uom_qty,
					'product_uom': line.product_uom.id,
					'location_id': so_picking_id.location_dest_id.id,
					'location_dest_id': self.default_location_id.id,
					'name': line.product_id.display_name,
					'sale_line_id': line.id,
				}
				move = self.env['stock.move'].create(move_vals)

				# Find existing move lines in original picking with lot for this product
				orig_move_lines = so_picking_id.move_line_ids.filtered(
					lambda ml: ml.product_id == line.product_id and ml.lot_id)

				if orig_move_lines:
					for ml in orig_move_lines:
						self.env['stock.move.line'].create({
							'move_id': move.id,
							'product_id': ml.product_id.id,
							'product_uom_id': ml.product_uom_id.id,
							'location_id': so_picking_id.location_dest_id.id,
							'location_dest_id': self.default_location_id.id,
							'lot_id': ml.lot_id.id,
							'quantity': ml.quantity,
						})
				else:
					self.env['stock.move.line'].create({
						'move_id': move.id,
						'product_id': line.product_id.id,
						'product_uom_id': line.product_uom.id,
						'location_id': so_picking_id.location_dest_id.id,
						'location_dest_id': self.default_location_id.id,
						'quantity': line.product_uom_qty,
					})

			if sale.procurement_group_id:
				picking_in.write({'group_id': sale.procurement_group_id.id})

			msg_body_in = _('Order Successfully Returned to Customer IN Picking %s') % picking_in.name
			sale.message_post(body=msg_body_in)

		# --- Outgoing Picking (Out Order) ---
		if picking_type_out:
			picking_out_vals = {
				'sale_id': sale.id,
				'origin': sale.name,
				'partner_id': sale.partner_id.id,
				'location_id': self.default_location_id.id,
				'location_dest_id': so_picking_id.location_dest_id.id,
				'picking_type_id': picking_type_out.id,
				'group_id': sale.procurement_group_id.id,
			}
			picking_out = stock_picking_model.create(picking_out_vals)

			for line in sale.order_line.filtered('create_repair_order'):
				move_vals = {
					'picking_id': picking_out.id,
					'product_id': line.product_id.id,
					'product_uom_qty': line.product_uom_qty,
					'product_uom': line.product_uom.id,
					'location_id': self.default_location_id.id,
					'location_dest_id': so_picking_id.location_dest_id.id,
					'name': line.product_id.display_name,
					'sale_line_id': line.id,
				}
				move = self.env['stock.move'].create(move_vals)

				orig_move_lines = so_picking_id.move_line_ids.filtered(
					lambda ml: ml.product_id == line.product_id and ml.lot_id)

				if orig_move_lines:
					for ml in orig_move_lines:
						self.env['stock.move.line'].create({
							'move_id': move.id,
							'product_id': ml.product_id.id,
							'product_uom_id': ml.product_uom_id.id,
							'location_id': self.default_location_id.id,
							'location_dest_id': so_picking_id.location_dest_id.id,
							'lot_id': ml.lot_id.id,
							'quantity': ml.quantity,
						})
				else:
					self.env['stock.move.line'].create({
						'move_id': move.id,
						'product_id': line.product_id.id,
						'product_uom_id': line.product_uom.id,
						'location_id': self.default_location_id.id,
						'location_dest_id': so_picking_id.location_dest_id.id,
						'quantity	': line.product_uom_qty,
					})

			if sale.procurement_group_id:
				picking_out.write({'group_id': sale.procurement_group_id.id})

			msg_body_out = _('Order Successfully Returned to Customer OUT Picking %s') % picking_out.name
			sale.message_post(body=msg_body_out)
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
			raise ValueError("No matching incoming picking found for the sale order.")
		incoming.ensure_one()

		picking_type_in = self.env['stock.picking.type'].search(
			[('code', '=', 'incoming')], limit=1
		)
		if not picking_type_in or not picking_type_in.sequence_id:
			raise ValueError("Incoming picking type or sequence is not properly configured.")

		# Create return picking
		return_picking_vals = {
			'sale_id': sale.id,
			'origin': sale.name,
			'partner_id': sale.partner_id.id,
			'location_id': incoming.location_dest_id.id,
			'location_dest_id': self.default_location_id.id,
			'picking_type_id': picking_type_in.id,
		}
		return_picking = stock_picking_model.create(return_picking_vals)

		# Add moves and move lines
		for line in sale.order_line.filtered('create_repair_order'):
			move = self.env['stock.move'].create({
				'picking_id': return_picking.id,
				'product_id': line.product_id.id,
				'product_uom_qty': line.product_uom_qty,
				'product_uom': line.product_uom.id,
				'location_id': incoming.location_dest_id.id,
				'location_dest_id': self.default_location_id.id,
				'name': line.product_id.name,
				'sale_line_id': line.id,
			})

			# Try to copy original lot info from incoming move lines
			orig_move_lines = incoming.move_line_ids.filtered(
				lambda ml: ml.product_id == line.product_id and ml.lot_id)

			if orig_move_lines:
				for orig_line in orig_move_lines:
					self.env['stock.move.line'].create({
						'move_id': move.id,
						'product_id': orig_line.product_id.id,
						'product_uom_id': orig_line.product_uom_id.id,
						'quantity': orig_line.quantity,
						'location_id': incoming.location_dest_id.id,
						'location_dest_id': self.default_location_id.id,
						'lot_id': orig_line.lot_id.id,
					})
			else:
				# No lots, create one basic move line
				self.env['stock.move.line'].create({
					'move_id': move.id,
					'product_id': line.product_id.id,
					'product_uom_id': line.product_uom.id,
					'quantity': line.product_uom_qty,
					'location_id': incoming.location_dest_id.id,
					'location_dest_id': self.default_location_id.id,
				})

		# Post message
		self.env['mail.message'].sudo().create({
			"message_type": 'comment',
			'model': 'sale.order',
			'res_id': sale.id,
			"body": _('Order Successfully Returned Out Order %s') % return_picking.name
		})

		return True








class RepairActionLineWizard(models.TransientModel):
	_name = 'repair.action.line.wizard'
	_description = "Repair Action Line Wizard"

	repair_action_id = fields.Many2one(
		'repair.action.wizard',
		string="Repair Action",
		ondelete='cascade'
	)
	product_id = fields.Many2one('product.product', string="Product")
	quantity = fields.Float(string="Quantity")
	lot_id = fields.Many2one('stock.lot', string="Lot/Serial Number")
