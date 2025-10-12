# -*- coding: utf-8 -*-
from odoo import api, models

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def message_post(self, **kwargs):
        res = super().message_post(**kwargs)
        body = kwargs.get("body")
        if body and not self.env.context.get("mail_auto_delete"):
            company_user = self.env.company.cf_user_ticket_id or self.env.user
            self.env["cf.productivity.line"].sudo().log_entry(
                user=company_user,
                type_key="ticket",
                reason="Ticket respondido",
                ref_model="helpdesk.ticket",
                ref_id=self.id,
            )
        return res
