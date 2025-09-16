from odoo import api, fields, models
import requests 

class SaleOrder(models.Model):
	_inherit = "sale.order"

	sync_status = fields.Selection([('failure_9', 'Fail Cancel Order'), ('failure_10', 'Fail Delivery'), ('done', 'Done')], string = "Sync Status", readonly=True)

	def action_cancel(self):
		res = super(SaleOrder, self).action_cancel()
		for sale in self:
			sale._notify_delivery_status()
		return res

	def _notify_delivery_status(self, status=9):
		# loginc for send request
		url = self.env.company.web_url
		if url and self.env.company.web_token:
			headers = {"Content-Type": "application/json", "X-Webhook-Token": self.env.company.web_token}
			payload = {
				"orders": [{
					"order_number": self.name,
					"status": status
				}]
			}
			try:
				answer = requests.post(url, data=payload, headers=headers)
				if answer.status_code == 200:
					self.sync_status = "done"
				else:
					self.sync_status = "failure"
			except requests.exceptions.ConnectionError:
				self.sync_status = "failure"
		return True

	@api.model
	def call_webhook_integration(self):
		failed_orders = self.env['sale.order'].search([('sync_status', 'in', ["failure9","failure10"])])
		for sale in failed_orders:
			if sale.sync_status == "failure9":
				sale._notify_delivery_status()
			else:
				sale._notify_delivery_status(status=10)
		return True


class StockPicking(models.Model):
	_inherit = "stock.picking"

	def button_validate(self):
		res = super(StockPicking, self).button_validate()
		for picking in self:
			if picking.sale_id:
				if picking.sale_id.delivery_status != "pending":
					picking.sale_id._notify_delivery_status(status=10)
		return res

	