from odoo import api, fields, models

class SaleCancelRequestWizard(models.TransientModel):
    _name = "sale.cancel.request.wizard"
    _description = "Wizard de solicitud de cancelación de OV"

    sale_id = fields.Many2one("sale.order", required=True, string="Pedido")
    reason = fields.Text("Motivo", required=True)

    def _get_approver_group(self):
        # Intentar por xmlid estándar
        group = self.env.ref("cfon_sale_cancel_request.group_cancel_approver", raise_if_not_found=False)
        if not group:
            # Intentar por posible nombre de carpeta distinto (p.ej. _final, _v7, etc.)
            group = self.env.ref("cfon_sale_cancel_request_final.group_cancel_approver", raise_if_not_found=False)
        if not group:
            # Buscar por nombre del grupo, por si se importó sin xmlid
            group = self.env["res.groups"].search([("name", "=", "Aprobadores de cancelación")], limit=1)
        if not group:
            # Fallback duro: usar managers de ventas
            group = self.env.ref("sales_team.group_sale_manager")
        return group

    def action_submit(self):
        self.ensure_one()
        sale = self.sale_id
        # Marca solicitud y guarda motivo
        sale.write({"cancel_request": True, "cancel_reason": self.reason})

        # Destinatarios: Aprobadores + Comercial de la OV (si existe)
        approver_group = self._get_approver_group()
        users_to_notify = approver_group.users
        if sale.user_id:
            users_to_notify |= sale.user_id

        partner_ids = users_to_notify.mapped("partner_id").ids
        if partner_ids:
            sale.message_subscribe(partner_ids=partner_ids)

        body = f"<b>Solicitud de cancelación</b><br/>{(self.reason or '').strip()}"
        sale.message_post(
            body=body,
            partner_ids=partner_ids,
            subtype_xmlid="mail.mt_comment",
        )

        for u in users_to_notify:
            sale.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=u.id,
                summary="Revisar solicitud de cancelación",
                note=self.reason,
            )

        return {"type": "ir.actions.act_window_close"}