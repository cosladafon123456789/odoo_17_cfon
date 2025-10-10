from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging, requests
from datetime import timedelta

_logger = logging.getLogger(__name__)

class MarketplaceAccount(models.Model):
    _name = "marketplace.account"
    _description = "Cuenta de Marketplace (Mirakl)"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    api_url = fields.Char(string="API Base URL", required=True, help="Ej: https://mediamarktsaturn.mirakl.net/api")
    api_key = fields.Char(string="API Key", required=True, help="Debe ser la clave del usuario ADMIN en Mirakl")
    shop_id = fields.Char(string="Shop/Seller ID", help="Seller ID numérico requerido por algunos Mirakl (PCComponentes, MediaMarkt, etc.)")
    active = fields.Boolean(default=True)
    last_sync = fields.Datetime(readonly=True)
    ticket_count = fields.Integer(compute="_compute_ticket_count")

    # -------------------------------
    # CONTADOR DE TICKETS
    # -------------------------------
    def _compute_ticket_count(self):
        for rec in self:
            rec.ticket_count = self.env["marketplace.ticket"].sudo().search_count([("account_id", "=", rec.id)])

    # -------------------------------
    # CABECERAS DE AUTENTICACIÓN
    # -------------------------------
    def _build_headers(self):
        """Cabeceras para Mirakl (MediaMarkt, PCComponentes, etc.)"""
        self.ensure_one()
        headers = {
            "Accept": "application/json",
            "User-Agent": "Odoo-Marketplace-Integration",
        }

        # MediaMarkt y la mayoría de Mirakl usan autenticación básica (Basic)
        if self.api_key:
            headers["Authorization"] = f"Basic {self.api_key.strip()}"
        else:
            raise UserError(_("Debe configurar la API Key para conectarse."))

        # Algunos Mirakl requieren además el Seller ID
        if self.shop_id:
            headers["X-MIRAKL-SELLER-ID"] = str(self.shop_id)

        return headers

    # -------------------------------
    # MÉTODOS API
    # -------------------------------
    def _api_get(self, path, params=None, timeout=60):
        self.ensure_one()
        url = (self.api_url or "").rstrip("/") + "/" + path.lstrip("/")
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
        self.ensure_one()
        url = (self.api_url or "").rstrip("/") + "/" + path.lstrip("/")
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

    # -------------------------------
    # ACCIONES EN INTERFAZ
    # -------------------------------
    def action_test_connection(self):
        """Botón 'Probar conexión'"""
        self.ensure_one()
        try:
            # Intentar obtener mensajes primero
            data = self._api_get("/api/messages", params={"max": 1})
            arr = data.get("messages") or data.get("data") or []
            self.message_post(body=_("✅ Conexión OK (messages). Elementos: %s") % (len(arr) if isinstance(arr, list) else 0))
        except Exception as e1:
            try:
                # Si falla, probar con /orders
                data = self._api_get("/api/orders", params={"max": 1})
                arr = data.get("orders") or data.get("data") or []
                self.message_post(body=_("⚠️ Messages no disponible. ✅ Conexión OK (orders). Elementos: %s") % (len(arr) if isinstance(arr, list) else 0))
            except Exception as e2:
                self.message_post(body=_("❌ Error de conexión: %s") % (e1 or e2))
                raise

    def action_view_tickets(self):
        """Botón 'Ver tickets'"""
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
        """Botón 'Sincronizar ahora'"""
        for acc in self:
            acc._sync_messages()

    # -------------------------------
    # SINCRONIZACIÓN DE MENSAJES
    # -------------------------------
    def _sync_messages(self):
        """Sincroniza mensajes desde Mirakl"""
        self.ensure_one()
        Ticket = self.env["marketplace.ticket"].sudo()
        Message = self.env["marketplace.message"].sudo()
        since_dt = self.last_sync or (fields.Datetime.now() - timedelta(days=7))
        params = {"max": 100, "since": fields.Datetime.to_string(since_dt)}

        data = self._api_get("/api/messages", params=params)
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

            self.env["marketplace.message"].create({
                "ticket_id": ticket.id,
                "external_id": msg_id or False,
                "author": author_name,
                "date": date_val,
                "direction": "in" if direction in ("in", "incoming", "customer") else "out",
                "body": body,
            })
            created_msgs += 1

        self.last_sync = fields.Datetime.now()
        self.message_post(body=_("Sincronización completada. Tickets nuevos: %s, Mensajes nuevos: %s") % (created_tickets, created_msgs))

    # -------------------------------
    # CRON AUTOMÁTICO
    # -------------------------------
    @api.model
    def _cron_sync(self):
        for acc in self.search([("active", "=", True)]):
            try:
                acc._sync_messages()
            except Exception as e:
                _logger.exception("Cron sync failed for account %s", acc.name)
                acc.message_post(body=_("❌ Cron fallo: %s") % e)
