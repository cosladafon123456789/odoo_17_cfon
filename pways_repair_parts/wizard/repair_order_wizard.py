from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date


class LotRepairOrderWizard(models.TransientModel):
	_name = 'lot.repair.order.wizard'
	_description = "Repair order Wizard"
	_inherit = ['mail.thread', 'mail.activity.mixin']

	quantity = fields.Float('Quantity')
	avl_quantity = fields.Float('Available Quantity')
	action_type = fields.Selection(
		[
			('repair', 'Repair'),
			('rma', 'RMA')
		],
		string="Action Type")
	stock_lot_id = fields.Many2one('stock.lot', string="Lot-id")
	delivery_ids = fields.Many2many('stock.picking', string='Transfers')
	picking_id = fields.Many2one('stock.picking', string="Picking", domain="[('id', 'in', delivery_ids)]")

	def action_create_lot(self):
		repair_order_model = self.env['repair.order']
		active_id = self.env.context.get('active_id')
		stock_lot_active_id = self.env['stock.lot'].browse(active_id)
		picking_data = self.env['stock.picking.type'].search([('code', '=', 'repair_operation')])        
		product_qty = stock_lot_active_id.product_qty

		if self.quantity > product_qty:
			raise ValidationError(_("Quantity can't be more that On Hand Quantity"))
		
		if self.quantity == 0:
			raise ValidationError(_("Quantity can't be Zero"))

		for rec in stock_lot_active_id:
			vals = {
				"stock_lot_id": stock_lot_active_id.id,
				"product_id": rec.product_id.id,
				"product_qty": self.quantity,
				"lot_id": stock_lot_active_id.id,
				"picking_type_id" : picking_data.id,
			}
			print('vals>>>>>>>>>>>>>>>>>>>>',vals)
			picking_type = self.env["stock.picking.type"].search([], limit=1)
			if not picking_type or not picking_type.sequence_id:
				raise ValueError(_("Picking type or sequence ID is not properly configured."))
			repair_order = repair_order_model.create(vals)
			msg_body = _('Orden de reparación creada con éxito : %s',repair_order.name)
			stock_lot_active_id.message_post(body=msg_body)

		return True

	@api.onchange('picking_id')
	def _onchange_picking_quantity(self):
		""" This method will set available quantity at customer place of specific outgoing shipment """
		lot_wise_dict = {}
		if self.picking_id.sale_id:
			for line in self.picking_id.sale_id.order_line.filtered(lambda x: x.product_id.id == self.stock_lot_id.product_id.id):
				if line.qty_delivered_method == 'stock_move':
					outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
					out_move_lines = outgoing_moves.mapped('move_line_ids').filtered(lambda x: x.lot_id.id == self.stock_lot_id.id)
					in_move_lines = incoming_moves.mapped('move_line_ids').filtered(lambda x: x.lot_id.id == self.stock_lot_id.id)
					for move_line in out_move_lines:
						if move_line.move_id.state == 'done' and move_line.lot_id:
							lot = move_line.lot_id
							lot_wise_dict[lot.id] = lot_wise_dict.get(lot.id, 0.0) + move_line.quantity
					for move_line in in_move_lines:
						if move_line.move_id.state == 'done' and move_line.lot_id:
							lot = move_line.lot_id
							if lot_wise_dict.get(lot.id, False):
								lot_wise_dict[lot.id] -= move_line.quantity
					print('lot_wise_dict',lot_wise_dict)
					print('sum(qty for qty in lot_wise_dict.values() if qty > 0)',sum(qty for qty in lot_wise_dict.values() if qty > 0))
			self.avl_quantity = sum(qty for qty in lot_wise_dict.values() if qty > 0)
		else:
			delivery = self.picking_id
			print('delivery>>>>>>>>>>>>>>>>>>>>>>>>>',delivery)
			lot_lines = delivery.mapped('move_line_ids').filtered(
				lambda ml: ml.product_id.id == self.stock_lot_id.product_id.id and ml.lot_id.id == self.stock_lot_id.id)
			print('lot_lines***************************',lot_lines)
			lot_quantity = sum(lot_lines.mapped('quantity'))
			print('lot_quantity>>>>>>>>>>>>>>>>>>>>>>>>>>>',lot_quantity)
			self.avl_quantity = lot_quantity


	def action_rma(self):
		stock_picking_model = self.env['stock.picking']
		stock_move_line_model = self.env['stock.move.line']
		rma_location = self.env['stock.warehouse'].search(
			[('company_id', '=', self.env.company.id)], limit=1).rma_location

		if not rma_location:
			raise ValidationError(_("You need to fill RMA Location in Warehouse"))

		delivery = self.picking_id
		sale = self.picking_id.sale_id

		if self.quantity == 0:
			raise ValidationError(_("Quantity can't be Zero"))

		if self.avl_quantity < self.quantity:
			raise ValidationError(_("You Can't Process more than Available Quantity"))

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

		picking_vals = {
			'sale_id': sale.id if sale else None,
			'origin': sale.name if sale and sale.name else (delivery.name if delivery else None),
			'partner_id': (
				sale.partner_id.id if sale and sale.partner_id else
				(delivery.partner_id.id if delivery and delivery.partner_id else None)),
			'location_id': delivery.location_dest_id.id,
			'location_dest_id': rma_location.id,
			'picking_type_id': picking_type_in.id,
			'group_id': (
				sale.procurement_group_id.id if sale and sale.procurement_group_id else
				(delivery.group_id.id if delivery and delivery.group_id else None)),
		}
		in_order = stock_picking_model.create(picking_vals)

		pro_move_id = delivery.move_ids_without_package.filtered(lambda x: x.product_id == self.stock_lot_id.product_id)
		print('pro_move_id<><><><><><><><><><><><>',pro_move_id)
		# raise ValidationError(_('Ruko bhai'))

		moves = self.env['stock.move']
		for line in self.stock_lot_id:
			if line.product_id.id not in moves.mapped('product_id').ids:
				moves |= self.env['stock.move'].create({
					'name': line.product_id.name,
					'product_id': line.product_id.id,
					'product_uom_qty': self.quantity,
					'product_uom': line.product_id.uom_id.id,
					'location_id': delivery.location_dest_id.id,
					'location_dest_id': rma_location.id,
					'picking_id': in_order.id,
					'sale_line_id': pro_move_id.sale_line_id.id,
					'origin_returned_move_id': pro_move_id.id,
					'to_refund': True
				})
			find_move = moves.filtered(lambda x: x.product_id == line.product_id)
			print(find_move)
			move_line = self.env['stock.move.line'].create({
				'move_id': find_move.id,
				'product_id': line.product_id.id,
				'product_uom_id': line.product_id.uom_id.id,
				'picking_id': find_move.picking_id.id, 
				'quantity': self.quantity,
				'location_id': find_move.location_id.id,
				'location_dest_id': find_move.location_dest_id.id,
				'lot_name': line.name,
				'lot_id': line.id,
			})
			print(move_line)

		if sale.procurement_group_id:
			in_order.write({'group_id': sale.procurement_group_id.id})
		in_order.action_confirm()
		in_order.button_validate() 

		# msg_body = _('Tus productos están en garantía y se enviaron correctamente al RMA : %s') % in_order.name
		# sale.message_post(body=msg_body)

		msg_body = _('Tus productos están en garantía y se enviaron correctamente al RMA : %s') % in_order.name
		self.stock_lot_id.message_post(body=msg_body)

		# sale.repair_status = 'rma'

		return True
