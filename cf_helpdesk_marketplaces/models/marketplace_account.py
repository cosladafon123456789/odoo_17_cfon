
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests, logging
from datetime import timedelta

_logger = logging.getLogger(__name__)

class MarketplaceAccount(models.Model):
    _name = "marketplace.account"
    _description = "Cuenta de Marketplace (MediaMarkt Mirakl)"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, default="MediaMarkt", tracking=True)
    api_url = fields.Char(string="API Base URL", required=True, help="Ej: https://marketplace.api.mirakl.net")
    api_key = fields.Char(string="API Key", required=True)
    shop_id = fields.Char(string="Shop ID (si aplica)")
    active = fields.Boolean(default=True)
    last_sync = fields.Datetime(readonly=True)
    ticket_count = fields.Integer(compute="_compute_ticket_count")

    def _compute_ticket_count(self):
        for rec in self:
            rec.ticket_count = self.env["marketplace.ticket"].search_count([("account_id","=",rec.id)])

    def _build_headers(self):
        self.ensure_one()
        headers = {"X-API-KEY": self.api_key or ""}
        if self.shop_id:
            headers["X-SHOP-ID"] = self.shop_id
        return headers

    def _api_get(self, path, params=None):
        self.ensure_one()
        url = (self.api_url or '').rstrip('/') + '/' + path.lstrip('/')
        try:
            res = requests.get(url, headers=self._build_headers(), params=params, timeout=60)
            if not res.ok:
                raise UserError(_("Error en la API: %s") % res.text)
            return res.json()
        except Exception as e:
            raise UserError(_("No se pudo conectar con la API: %s") % e)

    def _api_post(self, path, payload=None, files=None):
        self.ensure_one()
        url = (self.api_url or '').rstrip('/') + '/' + path.lstrip('/')
        try:
            if files:
                res = requests.post(url, headers=self._build_headers(), data=payload, files=files, timeout=60)
            else:
                res = requests.post(url, headers=self._build_headers(), json=payload, timeout=60)
            if not res.ok:
                raise UserError(_("Error al enviar mensaje: %s") % res.text)
            return res.json()
        except Exception as e:
            raise UserError(_("Error de conexión: %s") % e)

    def action_test_connection(self):
        self.ensure_one()
        try:
            data = self._api_get("/api/messages", params={"max": 1})
            count = len(data.get("messages", [])) if isinstance(data, dict) else 0
            self.message_post(body=_("✅ Conexión correcta con MediaMarkt. Mensajes detectados: %s") % count)
        except Exception as e:
            self.message_post(body=_("❌ Error en la conexión: %s") % e)
            raise

    def action_sync_now(self):
        for acc in self:
            acc._sync_messages()

    def _sync_messages(self):
        Ticket = self.env["marketplace.ticket"].sudo()
        Message = self.env["marketplace.message"].sudo()
        since = self.last_sync or (fields.Datetime.now() - timedelta(days=7))
        data = self._api_get("/api/messages", params={"max": 100, "since": since.strftime('%Y-%m-%dT%H:%M:%SZ')})
        messages = data.get("messages", []) if isinstance(data, dict) else []
        for msg in messages:
            ext_id = msg.get("id") or msg.get("thread_id")
            if not ext_id:
                continue
            ticket = Ticket.search([("external_id","=",ext_id),("account_id","=",self.id)], limit=1)
            if not ticket:
                ticket = Ticket.create({
                    "name": msg.get("subject") or "Sin asunto",
                    "external_id": ext_id,
                    "account_id": self.id,
                    "partner_id": False,
                    "marketplace_name": "MediaMarkt",
                })
            Message.create({
                "ticket_id": ticket.id,
                "external_id": msg.get("message_id"),
                "author": msg.get("author",{}).get("name","Cliente"),
                "body": msg.get("body",""),
                "direction": "in",
            })
        self.last_sync = fields.Datetime.now()
        self.message_post(body=_("Sincronización completada (%s mensajes)." % len(messages)))

    @api.model
    def _cron_sync(self):
        for acc in self.search([("active","=",True)]):
            acc._sync_messages()
