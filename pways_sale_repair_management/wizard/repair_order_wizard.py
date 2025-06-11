from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date


class RepairOrderWizard(models.TransientModel):
	_name = 'repair.order.wizard'
	_description = "Repair order Wizard"
	_inherit = ['mail.thread', 'mail.activity.mixin']

	description_1 = fields.Char(string="Description")
	description_2 = fields.Text(string="Quoatation Notes")

	def action_print_wizard(self):
		repair_order_model = self.env['repair.order']
		active_id = self.env.context.get('active_id')
		sale_order_active_id = self.env['sale.order'].browse(active_id)
		picking_data = self.env['stock.picking.type'].search([('code', '=', 'repair_operation')])
		for rec in sale_order_active_id.order_line:
			if rec.create_repair_order:
				vals = {
					"internal_notes": self.description_1,
					"sale_order_id": sale_order_active_id.id,
					"product_id": rec.product_id.id,
					"product_qty": rec.product_uom_qty,
					'product_uom': rec.product_uom.id,
					"partner_id": sale_order_active_id.partner_id.id,					
					"sale_order_line_id": rec.id,
					"picking_type_id" : sale_order_active_id.warehouse_id.repair_type_id.id,
				}

				# Check picking_type and sequence
				# picking_type = self.env["stock.picking.type"].search([], limit=1)
				# if not picking_type or not picking_type.sequence_id:
				# 	raise ValueError(_("Picking type or sequence ID is not properly configured."))

				# vals["name"] = picking_type.sequence_id.next_by_id()

				repair_order = repair_order_model.create(vals)
				# message_rec = self.env['mail.message'].sudo().create({
				# "message_type": 'comment', 
				# 'model': 'sale.order', 
				# 'res_id': sale_order_active_id.id, 
				# "body": _('Orden de reparación creada con éxito : %s',repair_order.name)
				# })
				msg_body = _('Orden de reparación creada con éxito : %s',repair_order.name)
				sale_order_active_id.message_post(body=msg_body)
				sale_order_active_id.repair_status = 'repair'

		# Fetch created repair orders
		activities = self.env["repair.order"].sudo().search([("sale_order_id.name", "=", sale_order_active_id.name)])
		action = self.env["ir.actions.actions"]._for_xml_id("repair.action_repair_order_tree")
		action["domain"] = [("id", "in", activities.ids)]
		return action

