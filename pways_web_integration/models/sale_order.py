from odoo import api, fields, models
import requests
import json

class SaleOrder(models.Model):
	_inherit = "sale.order"

	sync_status = fields.Selection([
		('failure_9', 'Fail Cancel Order'),
		('failure_10', 'Fail Delivery'),
		('failure_11', 'Fail Refund'),
		('done', 'Done')
	], string="Sync Status", readonly=True, copy=False)

	def action_cancel(self):
		res = super(SaleOrder, self).action_cancel()
		for sale in self:
			sale._notify_delivery_status()
		return res

	def button_refund(self):
		res = super(SaleOrder, self).button_refund()
		for sale in self:
			sale._notify_delivery_status(status=11)
		return res

	def _notify_delivery_status(self, status=9):
		# lógica para enviar request
		url = self.env.company.web_url
		if url and self.env.company.web_token:
			headers = {
				"Content-Type": "application/json",
				"X-Webhook-Token": self.env.company.web_token
			}
			failure_status = "failure_" + str(status)
			payload = {
				"orders": [{
					"order_number": self.name,
					"status": status
				}]
			}

			try:
				payload = json.dumps(payload)
				answer = requests.post(url, data=payload, headers=headers)
				print("answer.........", answer)
				if answer.status_code == 200:
					self.sync_status = "done"
				else:
					self.sync_status = failure_status
			except requests.exceptions.ConnectionError:
				self.sync_status = failure_status
		return True

	@api.model
	def call_webhook_integration(self):
		failed_orders = self.env['sale.order'].search([
			('sync_status', 'in', ["failure_9", "failure_10", "failure_11"])
		])
		for sale in failed_orders:
			if sale.sync_status == "failure_9":
				sale._notify_delivery_status()
			elif sale.sync_status == "failure_10":
				sale._notify_delivery_status(status=10)
			elif sale.sync_status == "failure_11":
				sale._notify_delivery_status(status=11)
		return True


class StockPicking(models.Model):
	_inherit = "stock.picking"

	def button_validate(self):
		res = super(StockPicking, self).button_validate()
		for picking in self:
			if picking.sale_id and picking.sale_id.delivery_status != "pending":
				picking.sale_id._notify_delivery_status(status=10)
		return res
