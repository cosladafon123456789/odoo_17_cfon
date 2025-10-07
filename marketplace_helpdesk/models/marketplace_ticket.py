import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class MarketplaceTicket(models.Model):
    _name = "marketplace.ticket"
    _description = "Ticket de Marketplace"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "last_message_date desc, id desc"

    name = fields.Char(string="Asunto / Nombre", tracking=True, required=True)
    marketplace = fields.Char(string="Marketplace", tracking=True)
    account_id = fields.Many2one("marketplace.account", string="Cuenta", required=True, index=True)
    external_id = fields.Char(string="ID externo", index=True)
    customer_name = fields.Char(string="Cliente")
    customer_email = fields.Char(string="Email")
    state = fields.Selection([
        ("new", "Nuevo"),
        ("in_progress", "En proceso"),
        ("answered", "Respondido"),
        ("closed", "Cerrado"),
    ], default="new", tracking=True)

    participants = fields.Char(string="Participantes")
    message_count = fields.Integer(string="Mensajes")
    last_message_date = fields.Datetime(string="Último mensaje", index=True)
    thread_type = fields.Char(string="Tipo")
    is_critical = fields.Boolean(string="Crítico", default=False)

    last_external_update = fields.Datetime(string="Última actualización externa", readonly=True)

    _sql_constraints = [
        ("account_external_unique", "unique(account_id, external_id)", "El hilo ya existe para esta cuenta."),
    ]

    def action_mark_in_progress(self):
        self.write({"state": "in_progress"})

    def action_mark_closed(self):
        self.write({"state": "closed"})

    def action_sync_messages(self):
        for rec in self:
            rec._sync_one_thread_messages()

    def _sync_one_thread_messages(self):
        # placeholder para futuro
        return True

    @api.model
    def cron_sync_marketplaces(self):
        accounts = self.env["marketplace.account"].search([("active","=",True)])
        for acc in accounts:
            self._sync_account(acc)

    def _sync_account(self, acc):
        unread_only = bool(acc.sync_unread_only)
        if not acc.last_sync:
            acc.last_sync = fields.Datetime.now()
            return
        client = self.env["mirakl.client"]
        try:
            threads = client.fetch_threads(acc, updated_since=acc.last_sync, unread_only=unread_only, with_messages=True)
        except Exception as e:
            _logger.exception("Error al traer hilos Mirakl: %s", e)
            return

        for th in threads:
            self._upsert_thread_from_payload(acc, th)

        acc.last_sync = fields.Datetime.now()

    def _upsert_thread_from_payload(self, acc, th):
        ext_id = str(th.get("id") or th.get("thread_id") or "")
        if not ext_id:
            return
        vals = {}
        subject = th.get("subject") or th.get("title") or th.get("name") or _("Sin asunto")
        vals.update({
            "name": subject,
            "marketplace": acc.name or "Mirakl",
            "account_id": acc.id,
            "external_id": ext_id,
        })

        parts = th.get("participants") or []
        if isinstance(parts, list):
            pnames = []
            for p in parts:
                pnames.append(p.get("display_name") or p.get("name") or p.get("email") or "")
            vals["participants"] = ", ".join([p for p in pnames if p])
        else:
            vals["participants"] = ""

        msgs = th.get("messages") or []
        vals["message_count"] = len(msgs)
        last_dt = False
        for m in msgs:
            ts = m.get("date") or m.get("created_at") or m.get("timestamp")
            if ts:
                try:
                    dt = fields.Datetime.to_datetime(ts)
                except Exception:
                    dt = False
                if dt and (not last_dt or dt > last_dt):
                    last_dt = dt
        vals["last_message_date"] = last_dt or fields.Datetime.now()
        vals["last_external_update"] = th.get("updated_at") or fields.Datetime.now()

        vals["thread_type"] = th.get("type") or th.get("category") or ""
        crit = th.get("critical") or th.get("is_critical") or False
        if not crit:
            for m in msgs:
                pr = (m.get("priority") or "").lower()
                if pr in ("high", "urgent", "critical"):
                    crit = True
                    break
        vals["is_critical"] = bool(crit)

        customer = th.get("customer") or {}
        vals["customer_name"] = customer.get("name") or ""
        vals["customer_email"] = customer.get("email") or ""

        unread = th.get("unread_count") or th.get("unreadCount") or 0
        vals["state"] = "new" if unread else "answered"

        rec = self.search([("account_id","=",acc.id), ("external_id","=",ext_id)], limit=1)
        if rec:
            rec.write(vals)
        else:
            self.create(vals)
