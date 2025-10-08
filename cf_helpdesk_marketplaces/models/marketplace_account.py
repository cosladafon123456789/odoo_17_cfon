
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import requests
from datetime import timedelta

_logger = logging.getLogger(__name__)

class MarketplaceAccount(models.Model):
    _name = "marketplace.account"
    _description = "Cuenta de Marketplace (API)"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    platform = fields.Selection([("mirakl","Mirakl")], default="mirakl", required=True, tracking=True)
    api_url = fields.Char(string="API Base URL", required=True, help="Ej: https://marketplace.api.mirakl.net")
    api_key = fields.Char(string="API Key", required=True)
    shop_id = fields.Char(string="Shop ID (si aplica)")
    active = fields.Boolean(default=True)
    last_sync = fields.Datetime(readonly=True)
    ticket_count = fields.Integer(compute="_compute_ticket_count")

    def _compute_ticket_count(self):
        for rec in self:
            rec.ticket_count = self.env["marketplace.ticket"].sudo().search_count([("account_id","=",rec.id)])

    # ---------- API helpers ----------
    def _build_headers(self):
        self.ensure_one()
        headers = {}
        headers["X-API-KEY"] = self.api_key or ""
        if self.shop_id:
            headers["X-SHOP-ID"] = self.shop_id
        return headers

    def _api_get(self, path, params=None, timeout=60):
        self.ensure_one()
        url = (self.api_url or "").rstrip("/") + "/" + path.lstrip("/")
        headers = self._build_headers()
        _logger.info("⤴️ [Marketplace GET] %s params=%s", url, params)
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=timeout)
            _logger.info("⤵️ [Marketplace GET %s] status=%s", url, resp.status_code)
            if not resp.ok:
                self.message_post(body=_("GET %(url)s devolvió %(code)s: %(txt)s", url=url, code=resp.status_code, txt=resp.text[:1000]))
                raise UserError(_("Error API GET %s: %s") % (url, resp.text))
            try:
                return resp.json()
            except Exception:
                self.message_post(body=_("⚠️ La respuesta no es JSON. Texto: %s") % resp.text[:1000])
                return {}
        except Exception as e:
            _logger.exception("API GET error to %s", url)
            raise UserError(_("No se pudo conectar a la API: %s") % e)

    def _api_post(self, path, payload=None, files=None, timeout=60):
        self.ensure_one()
        url = (self.api_url or "").rstrip("/") + "/" + path.lstrip("/")
        headers = self._build_headers()
        try:
            if files:
                _logger.info("⤴️ [Marketplace POST multipart] %s payload_keys=%s", url, list((payload or {}).keys()))
                resp = requests.post(url, headers=headers, data=payload or {}, files=files, timeout=timeout)
            else:
                headers["Content-Type"] = "application/json"
                _logger.info("⤴️ [Marketplace POST json] %s payload=%s", url, payload)
                resp = requests.post(url, headers=headers, json=payload or {}, timeout=timeout)
            _logger.info("⤵️ [Marketplace POST %s] status=%s", url, resp.status_code)
            if not resp.ok:
                self.message_post(body=_("POST %(url)s devolvió %(code)s: %(txt)s", url=url, code=resp.status_code, txt=resp.text[:1000]))
                raise UserError(_("Error API POST %s: %s") % (url, resp.text))
            try:
                return resp.json() if resp.text else {}
            except Exception:
                return {"_text": resp.text}
        except Exception as e:
            _logger.exception("API POST error to %s", url)
            raise UserError(_("No se pudo conectar a la API: %s") % e)

    # ---------- Actions ----------
    def action_view_tickets(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Tickets de Marketplace"),
            "res_model": "marketplace.ticket",
            "view_mode": "tree,form,kanban,calendar,pivot,graph",
            "domain": [("account_id","=",self.id)],
            "context": {"default_account_id": self.id},
        }

    def action_test_connection(self):
        self.ensure_one()
        try:
            data = self._api_get("/api/messages", params={"max": 1})
            count = 0
            if isinstance(data, dict):
                arr = data.get("messages") or data.get("data") or []
                count = len(arr) if isinstance(arr, list) else 0
            self.message_post(body=_("✅ Conexión OK. Endpoint respondió con %s elemento(s).") % count)
        except Exception as e:
            self.message_post(body=_("❌ Error de conexión: %s") % e)
            raise

    def action_sync_now(self):
        for acc in self:
            acc._sync_messages()

    def _sync_messages(self):
        self.ensure_one()
        Ticket = self.env["marketplace.ticket"].sudo()
        Message = self.env["marketplace.message"].sudo()

        since_dt = self.last_sync or (fields.Datetime.now() - timedelta(days=7))
        params = {"max": 100, "since": fields.Datetime.to_string(since_dt)}
        path = "/api/messages"
        data = self._api_get(path, params=params)

        messages = []
        if isinstance(data, dict):
            messages = data.get("messages") or data.get("data") or []
        if not isinstance(messages, list):
            messages = []

        created_tickets = 0
        created_msgs = 0

        for m in messages:
            ext_thread = str(m.get("thread_id") or m.get("id") or m.get("conversation_id") or "").strip()
            subject = (m.get("subject") or m.get("title") or _("Sin asunto")).strip()
            order_ref = (m.get("order_id") or m.get("order_reference") or "")

            partner_name, partner_email = None, None
            customer = m.get("customer")
            if isinstance(customer, dict):
                partner_name = (customer.get("name") or "").strip() or None
                partner_email = (customer.get("email") or "").strip() or None

            partner = False
            if partner_email:
                partner = self.env["res.partner"].search([("email","=",partner_email)], limit=1)
            if not partner and partner_name:
                partner = self.env["res.partner"].create({"name": partner_name, "email": partner_email})

            if not ext_thread:
                _logger.warning("Mensaje sin thread_id/id. Se ignora: %s", m)
                continue

            ticket = Ticket.search([("external_id","=",ext_thread),("account_id","=",self.id)], limit=1)
            if not ticket:
                ticket = Ticket.create({
                    "name": subject or _("Sin asunto"),
                    "external_id": ext_thread,
                    "account_id": self.id,
                    "order_reference": order_ref or False,
                    "partner_id": partner.id if partner else False,
                })
                created_tickets += 1

            msg_id = str(m.get("message_id") or m.get("id") or "").strip()
            if msg_id:
                exists = Message.search([("external_id","=",msg_id),("ticket_id","=",ticket.id)], limit=1)
                if exists:
                    continue

            body = (m.get("body") or m.get("message") or "").strip()
            author = m.get("author") or m.get("sender") or {}
            author_name = (author.get("name") if isinstance(author, dict) else str(author)) or _("Desconocido")
            direction = (m.get("direction") or "in").lower()
            date_val = m.get("date") or m.get("created_at") or fields.Datetime.now()

            Message.create({
                "ticket_id": ticket.id,
                "external_id": msg_id or False,
                "author": author_name,
                "date": date_val,
                "direction": "in" if direction in ("in","incoming","customer") else "out",
                "body": body,
            })
            created_msgs += 1

        self.last_sync = fields.Datetime.now()
        note = _("Sincronización finalizada. Tickets nuevos: %(t)s, Mensajes nuevos: %(m)s", t=created_tickets, m=created_msgs)
        self.message_post(body=note)
        _logger.info("[Marketplace Sync] %s", note)

    @api.model
    def _cron_sync(self):
        accounts = self.search([("active","=",True)])
        for acc in accounts:
            try:
                acc._sync_messages()
            except Exception as e:
                _logger.exception("Cron sync failed for account %s", acc.name)
                acc.message_post(body=_("❌ Cron fallo en %s: %s") % (acc.name, e))
