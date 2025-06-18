# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, SUPERUSER_ID
from collections import defaultdict
from odoo.exceptions import ValidationError
from datetime import date
from datetime import timedelta


class PurchaseOrderInherit(models.Model):
	_inherit = 'purchase.order'

	is_warranty = fields.Boolean('Garantia')
	warranty_period = fields.Float(
		string='Garantia Period (Days)',
		store=True
	)
	warranty_expiry_date = fields.Date(
		string='Garantia Hasta"',
		compute='_compute_warranty_expiry',
		store=True
	)

	@api.onchange('partner_id')
	def _onchange_warranty_period(self):
		for po in self:
			po.warranty_period = po.partner_id.warranty_period or 0.0


	@api.depends('warranty_period', 'date_order')
	def _compute_warranty_expiry(self):
		for po in self:
			if po.warranty_period and po.date_order:
				order_date = fields.Date.to_date(po.date_order)
				po.warranty_expiry_date = order_date + timedelta(days=po.warranty_period)
			else:
				po.warranty_expiry_date = False

	@api.constrains('warranty_period')
	def _check_warranty_period(self):
		for po in self:
			if po.warranty_period > 999:
				raise ValidationError("Warranty Period cannot exceed 999 days.")


class PurchaseOrderLineInherit(models.Model):
	_inherit = 'purchase.order.line'

	expiry_date = fields.Date(related='order_id.warranty_expiry_date')

	def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
		res = super()._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
		res.update({
			'date_force_expiry': self.expiry_date
		})
		return res