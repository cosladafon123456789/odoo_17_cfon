# -*- coding: utf-8 -*-
from odoo import models

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def message_post(self, **kwargs):
        res = super().message_post(**kwargs)
        body = kwargs.get("body")
        # Registrar sólo cuando es un mensaje con cuerpo y un usuario interno
        if body and self.env.user and not self.env.user._is_public():
            try:
                self.env["cf.productivity.line"].sudo().log_entry(
                    user=self.env.user,
                    type_key="ticket",
                    reason="Ticket respondido",
                    ref_model="helpdesk.ticket",
                    ref_id=self.id,
                )
            except Exception:
                # Nunca bloquear el post de mensajes por errores de log
                pass
        return res
