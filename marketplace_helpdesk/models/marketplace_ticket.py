# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class MarketplaceTicket(models.Model):
    _name = "marketplace.ticket"
    _description = "Ticket de Marketplace"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(string="Asunto", required=True, tracking=True)
    account_id = fields.Many2one("marketplace.account", required=True, tracking=True, string="Cuenta")
    external_id = fields.Char("ID conversación externo", index=True)
    customer_name = fields.Char("Cliente", tracking=True)
    customer_email = fields.Char("Email")
    state = fields.Selection([
        ("new","Nuevo"),
        ("in_progress","En proceso"),
        ("answered","Respondido"),
        ("closed","Cerrado")
    ], default="new", tracking=True)
    last_external_update = fields.Datetime("Última actualización remota")
    marketplace = fields.Char("Marketplace")
    can_send = fields.Boolean(compute="_compute_can_send")

    def _compute_can_send(self):
        for r in self:
            r.can_send = bool(r.external_id and r.account_id)

    def action_mark_in_progress(self):
        self.write({"state":"in_progress"})

    def action_mark_closed(self):
        self.write({"state":"closed"})

    def action_sync_messages(self):
        for ticket in self:
            ticket._sync_thread()

    def _sync_thread(self):
        self.ensure_one()
        client = self.env["mirakl.client"]
        ep, data = client.fetch_conversation_messages(self.account_id, self.external_id)
        if not data:
            return
        # Intentar mapear según API (conversations vs legacy)
        messages = []
        if isinstance(data, dict):
            if "messages" in data:
                messages = data.get("messages") or []
            elif "conversation" in data and isinstance(data.get("conversation"), dict):
                messages = data["conversation"].get("messages") or []
        elif isinstance(data, list):
            messages = data
        # Postear en chatter si no existe
        for m in messages:
            body = m.get("body") or m.get("message") or ""
            mid = str(m.get("id") or m.get("message_id") or "")
            author = m.get("author") or m.get("from") or {}
            author_name = author.get("name") if isinstance(author, dict) else (author or "Cliente")
            external_msg_key = f"mirakl:{self.external_id}:{mid}"
            # evitar duplicados usando message.reference (model data)
            already = self.message_ids.filtered(lambda x: external_msg_key in (x.message_type or "") or x.subject == external_msg_key)
            if already:
                continue
            self.message_post(
                body=f"<p><b>{author_name}</b></p><p>{body}</p>",
                subject=external_msg_key,
                message_type="comment",
                subtype_xmlid="mail.mt_comment"
            )

    def message_post(self, **kwargs):
        # interceptar envíos desde Odoo al cliente
        res = super().message_post(**kwargs)
        for rec in self:
            if kwargs.get("message_type") == "comment" and rec.external_id and rec.account_id and self.env.user.has_group("base.group_user"):
                body_plain = kwargs.get("body") or ""
                # Eliminar HTML simple
                import re
                body_clean = re.sub("<[^<]+?>", "", body_plain).strip()
                if body_clean:
                    ok, _resp = self.env["mirakl.client"].send_message(rec.account_id, rec.external_id, body_clean)
                    if ok:
                        rec.state = "answered"
                    else:
                        raise UserError(_("No se pudo enviar el mensaje a Mirakl. Revisa credenciales y endpoints."))
        return res

    @api.model
    def cron_sync_marketplaces(self):
        accounts = self.env["marketplace.account"].search([("active","=",True)])
        client = self.env["mirakl.client"]
        for acc in accounts:
            ep, data = client.fetch_new_conversations(acc, updated_since=acc.last_sync)
            conversations = []
            if isinstance(data, dict):
                conversations = data.get("conversations") or data.get("messages") or []
            elif isinstance(data, list):
                conversations = data
            for c in conversations:
                conv_id = str(c.get("id") or c.get("conversation_id") or c.get("message_id"))
                subject = c.get("subject") or c.get("topic") or "Mensaje Marketplace"
                customer_name = (c.get("customer") or {}).get("name") if isinstance(c.get("customer"), dict) else c.get("customer_name")
                vals = {
                    "name": subject,
                    "account_id": acc.id,
                    "external_id": conv_id,
                    "customer_name": customer_name or "Cliente",
                    "marketplace": acc.marketplace or acc.name,
                    "state": "new"
                }
                ticket = self.search([("external_id","=",conv_id),("account_id","=",acc.id)], limit=1)
                if ticket:
                    ticket.write({"name": subject})
                else:
                    ticket = self.create(vals)
                # sincronizar mensajes de cada ticket
                ticket._sync_thread()
            acc.last_sync = fields.Datetime.now()
