# -*- coding: utf-8 -*-
from odoo import api, models

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def message_post(self, **kwargs):
        res = super().message_post(**kwargs)
        # Contabiliza cuando el usuario envía un mensaje (comentario)
        # Evita duplicar en mensajes automáticos
        subtype = kwargs.get("subtype_id")
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

def write(self, vals):
    stage_changed = 'stage_id' in vals
    # Guardar nombres de etapa antes del cambio
    stage_names_before = {}
    if stage_changed:
        stage_map = {s.id: s.name for s in self.env['helpdesk.stage'].sudo().search([])}
        for t in self:
            stage_names_before[t.id] = t.stage_id.name or False

    res = super().write(vals)

    if stage_changed:
        stage_map = {s.id: s.name for s in self.env['helpdesk.stage'].sudo().search([])}
        company_user = self.env.company.cf_user_ticket_id or self.env.user
        for t in self:
            before = stage_names_before.get(t.id) or "—"
            after = stage_map.get(t.stage_id.id) or "—"
            if before != after:
                try:
                    self.env['cf.productivity.line'].sudo().log_entry(
                        user=company_user,
                        type_key='ticket',
                        reason=f"Cambio de etapa: {before} → {after}",
                        ref_model='helpdesk.ticket',
                        ref_id=t.id,
                    )
                except Exception:
                    # Nunca bloquear el write de ticket por esta métrica
                    pass
    return res
