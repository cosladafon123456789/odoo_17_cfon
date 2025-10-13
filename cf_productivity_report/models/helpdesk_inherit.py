# -*- coding: utf-8 -*-
from odoo import api, models

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def write(self, vals):
        stage_change = 'stage_id' in vals
        old_stages = {}
        if stage_change:
            for t in self:
                old_stages[t.id] = t.stage_id and t.stage_id.display_name or False

        res = super().write(vals)

        if stage_change:
            for t in self:
                try:
                    new_stage = t.stage_id and t.stage_id.display_name or False
                    old_stage = old_stages.get(t.id)
                    if new_stage and old_stage and new_stage != old_stage:
                        company_user = self.env.company.cf_user_ticket_id or self.env.user
                        self.env['cf.productivity.line'].sudo().log_entry(
                            user=company_user,
                            type_key='ticket_stage',
                            reason=f"{old_stage} → {new_stage}",
                            ref_model='helpdesk.ticket',
                            ref_id=t.id,
                        )
                except Exception:
                    continue
        return res

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
