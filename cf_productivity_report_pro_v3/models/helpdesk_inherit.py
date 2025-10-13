
# -*- coding: utf-8 -*-
from odoo import models

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
                reason="Mensaje enviado en ticket",
                ref_model="helpdesk.ticket",
                ref_id=self.id,
            )
        return res

    def write(self, vals):
        stage_changed_records = self.browse()
        if "stage_id" in vals:
            for rec in self:
                if rec.stage_id.id != vals.get("stage_id"):
                    stage_changed_records |= rec
        res = super().write(vals)
        if stage_changed_records:
            for rec in stage_changed_records:
                try:
                    company_user = rec.env.company.cf_user_ticket_id or rec.user_id or rec.env.user
                    stage_name = rec.stage_id.name or "Etapa actualizada"
                    rec.env["cf.productivity.line"].sudo().log_entry(
                        user=company_user if getattr(company_user, "_name", "") == 'res.users' else rec.env.user,
                        type_key="ticket",
                        reason=f"Cambio de etapa a {stage_name}",
                        ref_model="helpdesk.ticket",
                        ref_id=rec.id,
                    )
                except Exception:
                    continue
        return res
