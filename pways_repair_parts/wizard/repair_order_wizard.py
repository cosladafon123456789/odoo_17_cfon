from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date


class LotRepairOrderWizard(models.TransientModel):
	_name = 'lot.repair.order.wizard'
	_description = "Repair order Wizard"
	_inherit = ['mail.thread', 'mail.activity.mixin']

	quantity = fields.Float('Qty')
	avl_quantity = fields.Float('Available Qty')
	action_type = fields.Selection([('repair', 'Repair'),('rma', 'RMA')],string="Action Type")
	stock_lot_id = fields.Many2one('stock.lot', string="Lot-Repair-ID")
	location_ids = fields.Many2many('stock.location', string='Locations', compute="get_location_ids", store=True)
	location_id = fields.Many2one('stock.location', string="Location", domain="[('usage', '=', 'internal')]")
	delivery_ids = fields.Many2many('stock.picking', string='Transfers')
	picking_id = fields.Many2one('stock.picking', string="Picking", domain="[('id', 'in', delivery_ids)]")
	vendor_ids = fields.Many2many('res.partner', string="Vendors", compute="get_vendor_ids", store=True)
	vendor_id = fields.Many2one('res.partner', string="Vendor", domain="[('id', 'in', vendor_ids)]")


	# @api.model
	# def default_get(self, fields):
	# 	res = super().default_get(fields)
	# 	partner_ids = self.picking_id.product_id.mapped('seller_ids')
	# 	# self.partner_ids = partner_ids.ids
	# 	res.update({'partner_ids': partner_ids.ids}) 
	# 	return res

	@api.onchange('location_id')
	def _onchange_location_quantity(self):
		if self.location_id:
			lot_quantity = sum(self.location_id.quant_ids.filtered(lambda x:x.product_id == self.stock_lot_id.product_id and x.location_id.usage == 'internal').mapped('quantity'))
			self.avl_quantity = lot_quantity

	@api.depends('picking_id')
	def get_vendor_ids(self):
		for rec in self:
			partner_ids = rec.picking_id.product_id.mapped('seller_ids').mapped('partner_id')
			if not partner_ids:
				partner_ids = rec.stock_lot_id.product_id.mapped('seller_ids').mapped('partner_id')
			rec.vendor_ids = partner_ids.ids

	@api.depends('stock_lot_id.quant_ids')
	def get_location_ids(self):
		for rec in self:
			location_ids = rec.stock_lot_id.quant_ids.filtered(lambda x:x.product_id == rec.stock_lot_id.product_id and x.location_id.usage == 'internal').mapped('location_id')
			rec.location_ids = location_ids.ids

	def action_process(self, stock_lot_active_id, warehouse_id,repair_loc_id,product_qty):
		picking_type = warehouse_id.int_type_id
		group_id = self.env['procurement.group'].sudo().create({'name': stock_lot_active_id.name})
		out_moves = self.env['stock.move']
		for line in stock_lot_active_id:
			stock_to_transit = self.env['stock.move'].create({
				'name': line.product_id.name,
				'product_id': line.product_id.id,
				'origin': line.name,
				'location_id': self.location_id.id,
				'location_dest_id': repair_loc_id.id,
				'product_uom_qty': self.quantity,
				'quantity': self.quantity,
				'product_uom': line.product_uom_id.id,
				'picking_type_id': picking_type.id,
				'group_id': group_id.id,
			})
			stock_to_transit._assign_picking()
			if stock_to_transit.move_line_ids:
				stock_to_transit.move_line_ids.unlink()

			move_line_line = self.env['stock.move.line'].create({
				'move_id': stock_to_transit.id,
				'product_id': line.product_id.id,
				'product_uom_id': line.product_id.uom_id.id,
				'picking_id': stock_to_transit.picking_id.id, 
				'quantity': self.quantity,
				'location_id': stock_to_transit.location_id.id,
				'location_dest_id': stock_to_transit.location_dest_id.id,
				'lot_name': stock_lot_active_id.name,
				'lot_id': stock_lot_active_id.id,
			})
			stock_to_transit.picking_id.button_validate()
		return stock_to_transit

	def action_create_repair_from_lot(self):
		repair_order_model = self.env['repair.order']
		active_id = self.env.context.get('active_id')
		stock_lot_active_id = self.env['stock.lot'].browse(active_id)
		repair_type_id = self.env['stock.picking.type'].search([('code', '=', 'repair_operation')], limit=1)        
		product_qty = stock_lot_active_id.product_qty

		if not self.location_id:
			raise ValidationError(_("Please Select Source Location"))

		lot_quantity = sum(self.location_id.quant_ids.filtered(lambda x:x.product_id == self.stock_lot_id.product_id and x.location_id.usage == 'internal').mapped('quantity'))
		if lot_quantity and self.quantity and self.quantity > lot_quantity:
			raise ValidationError(_("product qty can not be greater than location wise available qty"))

		warehouse_id = repair_type_id.warehouse_id
		if self.location_id.warehouse_id:
			warehouse_id = self.location_id.warehouse_id

		if not warehouse_id.repair_loc_id:
			raise ValidationError(_("Please set repair location in warehouse"))


		if self.quantity > product_qty or self.quantity > self.avl_quantity:
			raise ValidationError(_("Qty can't be more that On Hand Qty"))
		
		if self.quantity == 0:
			raise ValidationError(_("Qty can't be Zero"))

		repair_loc_id = warehouse_id.repair_loc_id
		stock_move_id = self.action_process(stock_lot_active_id,warehouse_id,repair_loc_id,product_qty)
		
		if stock_move_id.picking_id:
			stock_move_id.picking_id.stock_lot_id = stock_lot_active_id.id
		
		for rec in stock_lot_active_id:
			vals = {
				"stock_picking_id": stock_move_id.picking_id and stock_move_id.picking_id.id,
				"product_id": rec.product_id.id,
				"product_qty": self.quantity,
				"lot_id": stock_lot_active_id.id,
				"picking_type_id" : warehouse_id.repair_type_id and warehouse_id.repair_type_id.id,
			}
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
			self.avl_quantity = sum(qty for qty in lot_wise_dict.values() if qty > 0)
		else:
			delivery = self.picking_id
			lot_lines = delivery.mapped('move_line_ids').filtered(lambda ml: ml.product_id.id == self.stock_lot_id.product_id.id and ml.lot_id.id == self.stock_lot_id.id)
			lot_quantity = sum(lot_lines.mapped('quantity'))
			self.avl_quantity = lot_quantity


	def action_rma(self):
		stock_picking_model = self.env['stock.picking']
		stock_move_line_model = self.env['stock.move.line']
		rma_location = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1).rma_location


		if not self.vendor_id:
			raise ValidationError(_("You need to Select Vendor from this rma"))
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

		picking_type_in = self.env['stock.picking.type'].search([('code', '=', 'incoming')], limit=1)

		picking_vals = {
			'sale_id': sale.id if sale else None,
			'origin': sale.name if sale and sale.name else (delivery.name if delivery else None),
			'partner_id': self.vendor_id.id,
			'location_id': delivery.location_dest_id.id,
			'location_dest_id': rma_location.id,
			'picking_type_id': picking_type_in.id,
			'is_rma': True,
			'group_id': (
				sale.procurement_group_id.id if sale and sale.procurement_group_id else
				(delivery.group_id.id if delivery and delivery.group_id else None)),
		}
		in_order = stock_picking_model.create(picking_vals)

		pro_move_id = delivery.move_ids_without_package.filtered(lambda x: x.product_id == self.stock_lot_id.product_id)

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

		if sale.procurement_group_id:
			in_order.write({'group_id': sale.procurement_group_id.id})

		msg_body = _('Tus productos están en garantía y se enviaron correctamente al RMA : %s') % in_order.name
		self.stock_lot_id.message_post(body=msg_body)

		return True
