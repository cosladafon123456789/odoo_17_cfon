
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import requests
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class MarketplaceAccount(models.Model):
    _name = "marketplace.account"
    _description = "Cuenta de Marketplace (API)"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    platform = fields.Selection([
        ("mirakl","Mirakl (genérico)"),
        ("custom","Custom")
    ], default="mirakl", required=True, tracking=True)
    api_url = fields.Char(string="API Base URL", required=True, help="Ej: https://marketplace.api.mirakl.net")
    api_key = fields.Char(string="API Key", required=True)
    shop_id = fields.Char(string="Shop ID (si aplica)")
    active = fields.Boolean(default=True)
    last_sync = fields.Datetime(readonly=True)
    ticket_count = fields.Integer(compute="_compute_ticket_count")

    def _compute_ticket_count(self):
        for rec in self:
            rec.ticket_count = self.env["marketplace.ticket"].sudo().search_count([("account_id","=",rec.id)])

    def action_view_tickets(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Tickets de Marketplace"),
            "res_model": "marketplace.ticket",
            "view_mode": "tree,form,kanban,calendar,pivot,graph",
            "domain": [("account_id","=",self.id)],
            "context": {"default_account_id": self.id},
        }

    # --- API helpers ---
    def _build_headers(self):
        headers = {}
        if self.platform == "mirakl":
            headers["X-API-KEY"] = self.api_key
            if self.shop_id:
                headers["X-SHOP-ID"] = self.shop_id
        else:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _api_get(self, path, params=None):
        self.ensure_one()
        url = (self.api_url.rstrip("/") + "/" + path.lstrip("/"))
        headers = self._build_headers()
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=60)
            if not resp.ok:
                raise UserError(_("Error API GET %s: %s") % (url, resp.text))
            return resp.json()
        except Exception as e:
            _logger.exception("API GET error")
            raise UserError(_("No se pudo conectar a la API: %s") % e)

    def _api_post(self, path, payload=None, files=None):
        self.ensure_one()
        url = (self.api_url.rstrip("/") + "/" + path.lstrip("/"))
        headers = self._build_headers()
        try:
            if files:
                resp = requests.post(url, headers=headers, data=payload or {}, files=files, timeout=60)
            else:
                headers["Content-Type"] = "application/json"
                resp = requests.post(url, headers=headers, json=payload or {}, timeout=60)
            if not resp.ok:
                raise UserError(_("Error API POST %s: %s") % (url, resp.text))
            return resp.json() if resp.text else {}
        except Exception as e:
            _logger.exception("API POST error")
            raise UserError(_("No se pudo conectar a la API: %s") % e)

    # --- Sync logic ---
    def action_sync_now(self):
        for acc in self:
            acc._sync_messages()

    def _sync_messages(self):
        self.ensure_one()
        # Basic Mirakl-like fetch. Adjust path/params to your marketplace.
        # Example: /api/messages?max=100&since=ISO8601
        since = (self.last_sync or (fields.Datetime.now() - timedelta(days=7)))
        params = {"max": 100, "since": fields.Datetime.to_string(since)}
        path = "/api/messages"
        data = self._api_get(path, params=params)
        # Expecting 'messages' array; adapt mapping as needed
        messages = data.get("messages") or data.get("data") or []
        Ticket = self.env["marketplace.ticket"].sudo()
        Message = self.env["marketplace.message"].sudo()

        created = 0
        for m in messages:
            ext_id = str(m.get("thread_id") or m.get("id") or m.get("conversation_id"))
            if not ext_id:
                continue
            ticket = Ticket.search([("external_id","=",ext_id),("account_id","=",self.id)], limit=1)
            if not ticket:
                subject = m.get("subject") or m.get("title") or _("Sin asunto")
                order_ref = m.get("order_id") or m.get("order_reference")
                partner_name = (m.get("customer") or {}).get("name") if isinstance(m.get("customer"), dict) else m.get("customer")
                partner_email = (m.get("customer") or {}).get("email") if isinstance(m.get("customer"), dict) else None
                partner = None
                if partner_email:
                    partner = self.env["res.partner"].search([("email","=",partner_email)], limit=1)
                if not partner and partner_name:
                    partner = self.env["res.partner"].create({"name": partner_name, "email": partner_email})
                ticket = Ticket.create({
                    "name": subject,
                    "external_id": ext_id,
                    "account_id": self.id,
                    "order_reference": order_ref,
                    "partner_id": partner.id if partner else False,
                })
                created += 1

            # create message if not present (key by remote message id + date)
            msg_id = str(m.get("id") or m.get("message_id") or "")
            existing = Message.search([("external_id","=",msg_id),("ticket_id","=",ticket.id)], limit=1) if msg_id else False
            if not existing:
                body = m.get("body") or m.get("message") or ""
                author = (m.get("author") or m.get("sender") or {})
                author_name = author.get("name") if isinstance(author, dict) else str(author)
                dir_in = (m.get("direction") or "").lower() in ("in","incoming","customer")
                date = m.get("date") or m.get("created_at") or fields.Datetime.now()
                Message.create({
                    "ticket_id": ticket.id,
                    "external_id": msg_id or False,
                    "author": author_name or _("Desconocido"),
                    "date": date,
                    "direction": "in" if dir_in else "out",
                    "body": body,
                })
        self.last_sync = fields.Datetime.now()
        self.message_post(body=_("Sincronización completada. Tickets nuevos: %s") % created)

    @api.model
    def _cron_sync(self):
        for acc in self.search([("active","=",True)]):
            try:
                acc._sync_messages()
            except Exception as e:
                _logger.exception("Cron sync failed for account %s", acc.name)
