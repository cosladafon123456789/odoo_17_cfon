from odoo import api, fields, models, _
from odoo.exceptions import UserError

MOTIVOS = [
    ('no_stock', 'No hay stock'),
    ('no_responde', 'Se ha llamado al cliente y no responde'),
    ('cliente_cancela', 'Cancelación por el cliente antes del envío'),
    ('direccion_imposible', 'No es posible realizar el envío a esa dirección'),
    ('otro', 'Otro motivo'),
]

class SaleCancelRequestWizard(models.TransientModel):
    _name = "sale.cancel.request.wizard"
    _description = "Wizard de solicitud de cancelación de OV"

    sale_id = fields.Many2one("sale.order", required=True, string="Pedido")
    reason_choice = fields.Selection(MOTIVOS, string="Motivo", required=True, default='no_stock')
    reason_other = fields.Text("Detalle del otro motivo")
    reason = fields.Text("Motivo (texto)", compute="_compute_reason", store=False)

    @api.depends('reason_choice', 'reason_other')
    def _compute_reason(self):
        label_map = dict(MOTIVOS)
        for w in self:
            base = label_map.get(w.reason_choice or '', '')
            if w.reason_choice == 'otro' and (w.reason_other or '').strip():
                w.reason = f"{base}: {w.reason_other.strip()}"
            else:
                w.reason = base

    def _get_approver_group(self):
        group = self.env.ref("cfon_sale_cancel_request.group_cancel_approver", raise_if_not_found=False)
        if not group:
            group = self.env.ref("cfon_sale_cancel_request_final.group_cancel_approver", raise_if_not_found=False)
        if not group:
            group = self.env['res.groups'].search([('name', '=', 'Aprobadores de cancelación')], limit=1)
        if not group:
            group = self.env.ref("sales_team.group_sale_manager")
        return group

    def action_submit(self):
        self.ensure_one()
        if self.reason_choice == 'otro' and not (self.reason_other or '').strip():
            raise UserError(_('Debes detallar el "Otro motivo".'))

        sale = self.sale_id
        final_reason = self.reason
        sale.write({
            "cancel_request": True,
            "cancel_reason": final_reason,
        })

        approver_group = self._get_approver_group()
        users_to_notify = approver_group.users
        if sale.user_id:
            users_to_notify |= sale.user_id

        partner_ids = users_to_notify.mapped("partner_id").ids
        if partner_ids:
            sale.message_subscribe(partner_ids=partner_ids)

        body = f"<b>Solicitud de cancelación</b><br/>{final_reason}"
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
                note=final_reason,
            )

        return {"type": "ir.actions.act_window_close"}