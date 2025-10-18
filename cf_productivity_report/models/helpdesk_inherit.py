# -*- coding: utf-8 -*-
from odoo import api, models

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def message_post(self, **kwargs):
        res = super().message_post(**kwargs)
        body = kwargs.get("body")
        if body and not self.env.context.get("mail_auto_delete") and self.env.user.name != "OdooBot":
            self.env["cf.productivity.line"].sudo().log_entry(
                user=self.env.user,
                type_key="ticket",
                reason="Ticket respondido",
                ref_model="helpdesk.ticket",
                ref_id=self.id,
            )
        return res

    def write(self, vals):
        stage_changed = "stage_id" in vals
        res = super().write(vals)
        if stage_changed and self.env.user.name != "OdooBot":
            for rec in self:
                stage = self.env["helpdesk.stage"].browse(vals.get("stage_id")) if vals.get("stage_id") else rec.stage_id
                if stage:
                    self.env["cf.productivity.line"].sudo().log_entry(
                        user=self.env.user,
                        type_key="ticket",
                        reason=f"Cambio de etapa a {stage.name}",
                        ref_model="helpdesk.ticket",
                        ref_id=rec.id,
                    )
        return res