# -*- coding: utf-8 -*-
from odoo import api, fields, models

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def message_post(self, **kwargs):
        res = super().message_post(**kwargs)
        # Count only when configured user posts a comment (Enviar)
        company = self.env.company
        if company.cf_user_ticket_id and company.cf_user_ticket_id.id == self.env.user.id:
            # message_type "comment" usually from "Enviar"
            msg_type = kwargs.get("message_type") or "comment"
            if msg_type == "comment":
                self.env["cf.productivity.line"].sudo().log_entry(
                    user=self.env.user,
                    type_key="ticket",
                    reason=None,
                    ref_model="helpdesk.ticket",
                    ref_id=self.id,
                )
        return res