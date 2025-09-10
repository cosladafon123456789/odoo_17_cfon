from odoo import api, fields, models

class SaleCancelRequestWizard(models.TransientModel):
    _name = "sale.cancel.request.wizard"
    _description = "Wizard de solicitud de cancelación de OV"

    sale_id = fields.Many2one("sale.order", required=True, string="Pedido")
    reason = fields.Text("Motivo", required=True)

    def action_submit(self):
        self.ensure_one()
        sale = self.sale_id
        # Marca solicitud y guarda motivo
        sale.write({"cancel_request": True, "cancel_reason": self.reason})

        # Destinatarios: TODOS los del grupo Aprobadores + el comercial del pedido
        approver_group = self.env.ref("cfon_sale_cancel_request.group_cancel_approver")
        users_to_notify = approver_group.users
        if sale.user_id:
            users_to_notify |= sale.user_id

        partner_ids = users_to_notify.mapped("partner_id").ids

        # Suscribir al hilo
        if partner_ids:
            sale.message_subscribe(partner_ids=partner_ids)

        # Mensaje en chatter (dispara notificaciones/email a seguidores)
        body = f"<b>Solicitud de cancelación</b><br/>{(self.reason or '').strip()}"
        sale.message_post(
            body=body,
            partner_ids=partner_ids,
            subtype_xmlid="mail.mt_comment",
        )

        # Actividades
        for u in users_to_notify:
            sale.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=u.id,
                summary="Revisar solicitud de cancelación",
                note=self.reason,
            )

        return {"type": "ir.actions.act_window_close"}