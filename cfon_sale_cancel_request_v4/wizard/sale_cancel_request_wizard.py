from odoo import api, fields, models

class SaleCancelRequestWizard(models.TransientModel):
    _name = "sale.cancel.request.wizard"
    _description = "Wizard de solicitud de cancelación de OV"

    sale_id = fields.Many2one("sale.order", required=True, string="Pedido")
    reason = fields.Text("Motivo", required=True)

    def action_submit(self):
        self.ensure_one()
        sale = self.sale_id
        sale.write({"cancel_request": True, "cancel_reason": self.reason})
        sale.message_post(body=f"<b>Solicitud de cancelación</b><br/>{(self.reason or '').strip()}")
        managers = self.env.ref("sales_team.group_sale_manager").users
        uid = managers[:1].id if managers else self.env.user.id
        sale.activity_schedule(
            "mail.mail_activity_data_todo",
            user_id=uid,
            summary="Revisar solicitud de cancelación",
            note=self.reason,
        )
        return {"type": "ir.actions.act_window_close"}