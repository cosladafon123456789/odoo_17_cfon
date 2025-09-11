from odoo import api, fields, models
import requests 

class SaleOrder(models.Model):
	_inherit = "sale.order"

	sync_status = fields.Selection([('failure', 'Failure'), ('done', 'Done')], string = "Sync Status", readonly=True)

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
					"status": status}]
			}
			try:
				answer = requests.post(url, data=payload, headers=headers)
				print("rrrrrrrrr", answer)
				self.sync_status = "done"
			except requests.exceptions.ConnectionError:
				self.sync_status = "failure"
				raise UserError("please check your internet connection.")
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

	