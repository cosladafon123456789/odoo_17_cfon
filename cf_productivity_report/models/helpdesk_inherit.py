# -*- coding: utf-8 -*-
from odoo import api, models

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def message_post(self, **kwargs):
        res = super().message_post(**kwargs)
        body = kwargs.get("body")
        # Registrar una línea de productividad cuando un usuario responde manualmente en un ticket
        if body and not self.env.context.get("mail_auto_delete"):
            self.env["cf.productivity.line"].sudo().log_entry(
                user=self.env.user,
                type_key="ticket",
                reason="Ticket respondido",
                ref_model="helpdesk.ticket",
                ref_id=self.id,
            )
        return res