from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import logging
from datetime import timedelta

_logger = logging.getLogger(__name__)


class MarketplaceAccount(models.Model):
    _name = "marketplace.account"
    _description = "Cuenta de Marketplace (Mirakl)"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    api_url = fields.Char(
        string="API Base URL",
        required=True,
        help="Ejemplo: https://mediamarktsaturn.mirakl.net/api o https://pccomponentes-prod.mirakl.net/api"
    )
    api_key = fields.Char(string="API Key", required=True, help="Clave API del usuario administrador en Mirakl")
    shop_id = fields.Char(string="Shop/Seller ID", help="ID numérico de la tienda (Seller ID)")
    active = fields.Boolean(default=True)
    last_sync = fields.Datetime(readonly=True)
    ticket_count = fields.Integer(compute="_compute_ticket_count")

    # ----------------------------------------------------
    # MÉTODOS AUXILIARES
    # ----------------------------------------------------

    def _compute_ticket_count(self):
        for rec in self:
            rec.ticket_count = self.env["marketplace.ticket"].sudo().search_count([("account_id", "=", rec.id)])

    def _build_headers(self):
        """Construye las cabeceras de autenticación para Mirakl"""
        self.ensure_one()
        headers = {
            "Accept": "application/json",
            "User-Agent": "Odoo-Marketplace-Integration",
        }
        # En la mayoría de Mirakl se usa X-API-KEY
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        # Algunos marketplaces (raro, pero posible) usan Authorization
        # headers["Authorization"] = f"Bearer {self.api_key}"
        if self.shop_id:
            headers["X-MIRAKL-SELLER-ID"] = str(self.shop_id)
        return headers

    def _api_get(self, path, params=None, timeout=60):
        """Petición GET genérica a la API Mirakl"""
        self.ensure_one()
        base = (self.api_url or "").rstrip("/")
        # Evita doble /api/api/
        if base.endswith("/api"):
            url = base + "/" + path.lstrip("/")
        else:
            url = base + "/api/" + path.lstrip("/")
        try:
            res = requests.get(url, headers=self._build_headers(), params=params or {}, timeout=timeout)
            if not res.ok:
                raise UserError(_("Error API GET %s: [%s] %s") % (url, res.status_code, res.text[:500]))
            try:
                return res.json()
            except Exception:
                raise UserError(_("La respuesta no es JSON válido: %s") % res.text[:500])
        except Exception as e:
            raise UserError(_("No se pudo conectar a la API: %s") % e)

    def _api_post(self, path, payload=None, files=None, timeout=60):
        """Petición POST genérica a la API Mirakl"""
        self.ensure_one()
        base = (self.api_url or "").rstrip("/")
        if base.endswith("/api"):
            url = base + "/" + path.lstrip("/")
        else:
            url = base + "/api/" + path.lstrip("/")
        try:
            if files:
                res = requests.post(url, headers=self._build_headers(), data=payload or {}, files=files, timeout=timeout)
            else:
                res = requests.post(url, headers=self._build_headers(), json=payload or {}, timeout=timeout)
            if not res.ok:
                raise UserError(_("Error API POST %s: [%s] %s") % (url, res.status_code, res.text[:500]))
            try:
                return res.json() if res.text else {}
            except Exception:
                return {"_text": res.text}
        except Exception as e:
            raise UserError(_("No se pudo conectar a la API: %s") % e)

    # ----------------------------------------------------
    # ACCIONES DEL USUARIO
    # ----------------------------------------------------

    def action_test_connection(self):
        """Comprueba la conexión con Mirakl probando endpoints accesibles para sellers"""
        self.ensure_one()
        try:
            # 🔹 1) Probar con /api/messages (siempre accesible a sellers)
            data = self._api_get("messages", params={"max": 1})
            arr = data.get("messages") or data.get("data") or []
            count = len(arr) if isinstance(arr, list) else 0
            self.message_post(body=_("✅ Conexión OK (messages). Elementos: %s") % count)
        except Exception as e1:
            try:
                # 🔹 2) Si falla, probar con /api/orders
                data = self._api_get("orders", params={"max": 1})
                arr = data.get("orders") or data.get("data") or []
                count = len(arr) if isinstance(arr, list) else 0
                self.message_post(body=_("✅ Conexión OK (orders). Elementos: %s") % count)
            except Exception as e2:
                msg = str(e1 or e2)
                self.message_post(body=_("❌ Error de conexión: %s") % msg)
                raise UserError(_("No se pudo conectar con la API: %s") % msg)

    def action_view_tickets(self):
        """Abre los tickets asociados a la cuenta"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Tickets de Marketplace"),
            "res_model": "marketplace.ticket",
            "view_mode": "kanban,tree,form,pivot,graph",
            "domain": [("account_id", "=", self.id)],
            "context": {"default_account_id": self.id},
        }

    def action_sync_now(self):
        """Sincroniza manualmente los mensajes"""
        for acc in self:
            acc._sync_messages()

    # ----------------------------------------------------
    # SINCRONIZACIÓN AUTOMÁTICA
    # ----------------------------------------------------

    def _sync_messages(self):
        """Sincroniza mensajes de Mirakl"""
        self.ensure_one()
        Ticket = self.env["marketplace.ticket"].sudo()
        Message = self.env["marketplace.message"].sudo()
        since_dt = self.last_sync or (fields.Datetime.now() - timedelta(days=7))
        params = {"max": 100, "since": fields.Datetime.to_string(since_dt)}
        data = self._api_get("messages", params=params)
        msgs = data.get("messages") or data.get("data") or []
        if not isinstance(msgs, list):
            msgs = []

        created_tickets = 0
        created_msgs = 0

        for m in msgs:
            ext_thread = str(m.get("thread_id") or m.get("id") or m.get("conversation_id") or "").strip()
            if not ext_thread:
                continue
            subject = (m.get("subject") or m.get("title") or _("Sin asunto")).strip()
            order_ref = (m.get("order_id") or m.get("order_reference") or "")
            partner = False
            customer = m.get("customer")
            if isinstance(customer, dict):
                email = (customer.get("email") or "").strip() or None
                name = (customer.get("name") or "").strip() or None
                if email:
                    partner = self.env["res.partner"].search([("email", "=", email)], limit=1)
                if not partner and (email or name):
                    partner = self.env["res.partner"].create({"name": name or email, "email": email})

            ticket = Ticket.search([("external_id", "=", ext_thread), ("account_id", "=", self.id)], limit=1)
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
                ex = self.env["marketplace.message"].search([("external_id", "=", msg_id), ("ticket_id", "=", ticket.id)], limit=1)
                if ex:
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
                "direction": "in" if direction in ("in", "incoming", "customer") else "out",
                "body": body,
            })
            created_msgs += 1

        self.last_sync = fields.Datetime.now()
        self.message_post(body=_("Sincronización completada. Tickets nuevos: %s, Mensajes nuevos: %s") %
                          (created_tickets, created_msgs))

    @api.model
    def _cron_sync(self):
        """Ejecutado automáticamente por cron"""
        for acc in self.search([("active", "=", True)]):
            try:
                acc._sync_messages()
            except Exception as e:
                _logger.exception("Cron sync failed for account %s", acc.name)
                acc.message_post(body=_("❌ Cron fallo: %s") % e)
