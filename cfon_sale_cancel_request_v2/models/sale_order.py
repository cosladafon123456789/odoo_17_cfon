from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    cancel_request = fields.Boolean(string="Solicitud de cancelación", default=False, tracking=True)
    cancel_reason = fields.Text(string="Motivo de cancelación", tracking=True)

    def action_request_cancel(self):
        self.ensure_one()
        return {
            "name": "Solicitar cancelación",
            "type": "ir.actions.act_window",
            "res_model": "sale.cancel.request.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_sale_id": self.id},
        }