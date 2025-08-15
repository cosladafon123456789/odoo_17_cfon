from odoo import fields, models, api, exceptions, _
from odoo.exceptions import ValidationError
from datetime import timedelta
import base64
from odoo import http
from odoo.http import request
from werkzeug.utils import redirect

class SaleOrder(models.Model):
	_inherit = "sale.order"
	
	# is_rebu = fields.Boolean(string='Es REBU')

	# x_studio_origen = fields.Char()

	def write(self, vals):
		result = super().write(vals)
		for order in self:
			if 'is_rebu' in vals:
				lines_to_update = order.order_line.filtered(lambda l: l.is_rebu != vals['is_rebu'])
				if lines_to_update:
					lines_to_update.write({'is_rebu': vals['is_rebu']})
		return result
	

class SaleOrderLine(models.Model):
	_inherit = "sale.order.line"


	# imei_ids = fields.Many2many('stock.lot',string='IMEI Number', copy=False, domain="[('product_id', '=', product_id)]")
	imei_ids = fields.Many2many('stock.lot',
		'sale_order_line_imei_rel', 
		'sale_line_id',
		'lot_id',
		string='IMEI Number',
		copy=False,
		domain="[('product_id', '=', product_id)]")
	tracking_number = fields.Char(string='Tracking Number',copy=False)
	picking_status = fields.Char(string="Shipping status", compute='_compute_picking_status', store=False)
	channel_web = fields.Char(related="order_id.origin",string="Channel (WEB)",copy=False)
	amount_total = fields.Monetary(related="order_id.amount_total",string='Total')
	invoice_status = fields.Selection(related="order_id.invoice_status",string='Invoice Status')
	date_order = fields.Datetime(related="order_id.date_order", string="Order Date")
	is_validated = fields.Boolean(string='Validated', copy=False)
	carrier_id = fields.Many2one('delivery.carrier',string='Transporista',copy=False)
	is_rebu = fields.Boolean(string='Es REBU', copy=False)
	attachment_id = fields.Many2one('ir.attachment',string="IMEI PDF", copy=False)
	country_id = fields.Many2one('res.country',string='Customer Country',related='order_id.partner_id.country_id')
	origen = fields.Char(related="order_id.x_studio_origen", string="Origen")
	picking_carrier_ids = fields.Many2many(
		'delivery.carrier',
		string='Transportistas',
		compute='_compute_carrier_ids', store=True,)
	picking_carrier_names = fields.Char(
		string="Carrier Names",
		compute="_compute_carrier_names",
		store=True,
	)
	has_carrier = fields.Boolean(string='Has Carrier',copy=False,compute='compute_has_carrier', store=True)


	@api.depends('move_ids.picking_id.carrier_id')
	def compute_has_carrier(self):
		for rec in self:
			pickings = rec.move_ids.mapped('picking_id')
			carrier_ids = pickings.mapped('carrier_id').ids
			rec.has_carrier = bool(pickings) and len(carrier_ids) == len(pickings)
   

	# @api.depends('move_ids')
	# def compute_has_carrier(self):
	#     for rec in self:
	#         carrier_id = rec.move_ids.mapped('picking_id').mapped('carrier_id')
	#         print('carrier_id.......................',carrier_id)
	#         if carrier_id:
	#             rec.has_carrier = True
	#             print('rec.has_carrier...................',rec.has_carrier)
	#         else:
	#             rec.has_carrier = False
	
	
	@api.depends('order_id.picking_ids.carrier_id')
	def _compute_carrier_ids(self):
		for line in self:
			carriers = line.order_id.picking_ids.mapped('carrier_id')
			line.picking_carrier_ids = carriers


	@api.depends('picking_carrier_ids')
	def _compute_carrier_names(self):
		for line in self:
			line.picking_carrier_names = ', '.join(line.picking_carrier_ids.mapped('name'))

	
	@api.depends('order_id.picking_ids.state')
	def _compute_picking_status(self):
		state_mapping = {
			'draft': 'Draft',
			'waiting': 'Waiting Another Operation',
			'confirmed': 'Waiting',
			'assigned': 'Ready',
			'done': 'Done',
			'cancel': 'Cancelled'
		}

		for line in self:
			pickings = line.order_id.picking_ids
			if pickings:
				states = [state_mapping.get(pick.state, pick.state) for pick in pickings]
				line.picking_status = ', '.join(states)
			else:
				line.picking_status = 'No Pickings'



	def _prepare_procurement_values(self, group_id=False):
		vals = super()._prepare_procurement_values(group_id=group_id)
		if self.imei_ids:
			vals["imei_ids"] = self.imei_ids.ids
		return vals


	def action_validation(self):
		for line in self:
			order = line.order_id
		
			lines_without_imei = order.order_line.filtered(lambda l: not l.imei_ids)

			if lines_without_imei:
				raise ValidationError("Please assign IMEI numbers for all order lines before validating.")


			if line.is_validated:
				raise ValidationError("This line has already validated.")

			# if not line.imei_ids:
			#     raise ValidationError("Please assign IMEI numbers before validating this line.")

			if order.state != 'sale':
				order.action_confirm()

			# if line.source_id:
			#     order.source_id = line.source_id

			related_moves = line.move_ids.filtered(lambda m: m.state not in ('done', 'cancel'))
			for move in related_moves:
				picking = move.picking_id
				if picking.state in ('done', 'cancel'):
					continue

				move.imei_ids = [(6, 0, line.imei_ids.ids)]

				move.move_line_ids.unlink()
				move._action_assign()

			for picking in order.picking_ids.filtered(lambda p: p.state not in ('done', 'cancel')):
				if line.carrier_id:
					picking.carrier_id = line.carrier_id
				
				for ml in picking.move_line_ids:
					if not ml.quantity:
						ml.quantity = ml.move_id.product_uom_qty or 1.0

				all_ready = all(ml.quantity for ml in picking.move_line_ids)

				if all_ready:
					picking.button_validate()

				if not picking.carrier_tracking_ref:
					if picking.carrier_id and picking.carrier_id.delivery_type == 'sendcloud_ts':
						picking.carrier_id.sendcloud_ts_send_shipping(picking)

				if picking.state == 'done':
					line.tracking_number = picking.carrier_tracking_ref
					# line.carrier_id = picking.carrier_id
					# line.imei_ids = [(6, 0, move.move_line_ids.mapped('lot_id').ids)]

				attachment_id = self.env['ir.attachment'].search([('res_id', '=', picking.id)], limit=1)

				if attachment_id:
					line.attachment_id = attachment_id.id
					download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
					# line.is_validated = True
					order.order_line.write({'is_validated': True})
					base_url = self.env['ir.config_parameter'].get_param('web.base.url')
					
					return {
						'type': 'ir.actions.act_url',
						'url': f'/attachment/open/{attachment_id.id}',
						'target': 'new',
					}
					# return {
					#     "type": "ir.actions.act_url",
					#     "url": str(base_url) + str(download_url),
					#     "target": "new",
					# }
				else:
					# line.is_validated = True
					order.order_line.write({'is_validated': True})

		
		return True


	@api.model
	def create(self, vals):
		line = super().create(vals)
		if vals.get('is_rebu') and line.order_id:
			line.order_id.is_rebu = True
		return line

	def write(self, vals):
		result = super().write(vals)
		for line in self:
			if 'is_rebu' in vals and line.order_id:
				# If any line is_rebu=True, mark order as rebu
				if any(l.is_rebu for l in line.order_id.order_line):
					line.order_id.is_rebu = True
				else:
					line.order_id.is_rebu = False
		return result



class StockMove(models.Model):
	_inherit = 'stock.move'

	imei_ids = fields.Many2many('stock.lot',string='Serial Numbers', domain="[('product_id', '=', product_id)]")

	def _prepare_procurement_values(self):
		vals = super()._prepare_procurement_values()
		vals["imei_ids"] = self.imei_ids.ids
		return vals

   

	def _action_assign(self):
		skip_moves = self.env['stock.move']
		res = super(StockMove, self)._action_assign()
		for move in self:
			if move.imei_ids:
				skip_moves |= move
				move.move_line_ids.unlink()
				
				for imei in move.imei_ids:
					move_line_vals = move._prepare_move_line_vals()
					move_line_vals['lot_id'] = imei.id

					move_line_vals['quantity'] = 1

					move_line = self.env['stock.move.line'].create(move_line_vals)
		return res




class StockRule(models.Model):
	_inherit = "stock.rule"

	def _get_custom_move_fields(self):
		fields = super()._get_custom_move_fields()
		fields += ["imei_ids"]
		return fields



class AttachmentOpenController(http.Controller):

	@http.route('/attachment/open/<int:attachment_id>', type='http', auth='user')
	def open_attachment(self, attachment_id):
		attachment = request.env['ir.attachment'].browse(attachment_id).sudo()
		if not attachment.exists():
			return redirect('/')
		file_content = base64.b64decode(attachment.datas) if attachment.datas else b""

		headers = [
			('Content-Type', attachment.mimetype or 'application/octet-stream'),
			('Content-Disposition', f'inline; filename="{attachment.name}"'),
		]
		return request.make_response(file_content, headers)




class StockPicking(models.Model):
	_inherit = "stock.picking"

	
	def button_validate(self):
		res = super(StockPicking, self).button_validate()
		for picking in self:
			sale_lines = picking.move_ids.sale_line_id
			
			attachment_id = self.env['ir.attachment'].search(
				[('res_id', '=', picking.id), ('res_model', '=', 'stock.picking')],
				limit=1
			)
			
			if sale_lines:
				for line in sale_lines:
					imei_lots = picking.move_line_ids.filtered(
						lambda ml: ml.move_id.sale_line_id == line
					).mapped('lot_id')
					
					line.write({
						'carrier_id': picking.carrier_id.id if picking.carrier_id else False,
						'tracking_number': picking.carrier_tracking_ref or False,
						'is_validated': True,
						'imei_ids': [(6, 0, imei_lots.ids)],
						'attachment_id': attachment_id.id if attachment_id else False,
					})
		return res

