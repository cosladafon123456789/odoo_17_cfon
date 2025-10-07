# -*- coding: utf-8 -*-
import logging
import requests
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MarketplaceAccount(models.Model):
    _name = "marketplace.account"
    _description = "Cuenta de Marketplace (Mirakl)"
    _rec_name = "name"

    # === Campos principales ===
    name = fields.Char(required=True)
    marketplace = fields.Selection([
        ("mediamarkt", "MediaMarkt"),
        ("pccomponentes", "PCComponentes"),
        ("carrefour", "Carrefour"),
        ("phonehouse", "Phone House"),
        ("otros", "Otros"),
    ], string="Marketplace")

    api_base = fields.Char(string="URL base API", required=True,
                           help="Ejemplo: https://mediamarktsaturn.mirakl.net/api")
    api_key = fields.Char(string="API Key", required=True)
    header_name = fields.Char(string="Nombre de cabecera",
                              default="Authorization",
                              help="Algunas instancias Mirakl usan X-API-Key o X-Mirakl-API-Key")

    last_sync = fields.Datetime(string="Última sincronización")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Compañía',
                                 default=lambda self: self.env.company, required=True)

    # === Endpoints configurables ===
    conv_list_endpoint = fields.Char(string="Endpoint listar conversaciones",
                                     default="/api/conversations")
    conv_messages_endpoint = fields.Char(string="Endpoint mensajes conversación",
                                         default="/api/conversations/{id}/messages")
    conv_send_message_endpoint = fields.Char(string="Endpoint enviar mensaje",
                                             default="/api/conversations/{id}/messages")
    legacy_messages_list_endpoint = fields.Char(string="Endpoint legacy listar mensajes",
                                                default="/api/messages")
    legacy_messages_thread_endpoint = fields.Char(string="Endpoint legacy hilo",
                                                  default="/api/messages/{id}")
    legacy_send_message_endpoint = fields.Char(string="Endpoint legacy responder",
                                               default="/api/messages/{id}/answer")

    # ========================================================================
    # MÉTODO PRINCIPAL DE SINCRONIZACIÓN (EJECUTADO POR EL CRON)
    # ========================================================================
    @api.model
    def cron_sync_marketplaces(self):
        """Sincroniza automáticamente las conversaciones de todas las cuentas activas."""
        _logger.info("==> [MARKETPLACE] Iniciando sincronización de marketplaces Mirakl...")

        accounts = self.search([("active", "=", True)])
        if not accounts:
            _logger.warning("No hay cuentas activas de marketplace configuradas.")
            return

        for account in accounts:
            try:
                account.sync_conversations()
            except Exception as e:
                _logger.exception(f"Error sincronizando cuenta {account.name}: {e}")

        _logger.info("==> [MARKETPLACE] Sincronización finalizada correctamente.")

    # ========================================================================
    # MÉTODO DE SINCRONIZACIÓN INDIVIDUAL POR CUENTA
    # ========================================================================
    def sync_conversations(self):
        """Llama a la API de Mirakl para obtener conversaciones nuevas."""
        self.ensure_one()

        headers = {
            self.header_name: self.api_key,
            "Accept": "application/json",
        }

        endpoints = [
            self.conv_list_endpoint or "/api/conversations",
            self.legacy_messages_list_endpoint or "/api/messages",
        ]

        success = False
        for ep in endpoints:
            url = f"{self.api_base.rstrip('/')}{ep}"
            _logger.info(f"==> [MARKETPLACE] Conectando con {url}")

            try:
                resp = requests.get(url, headers=headers, timeout=30)
            except Exception as e:
                _logger.exception(f"Error al conectar con {url}: {e}")
                continue

            if resp.status_code == 200:
                data = resp.json()
                self._process_conversations(data)
                success = True
                break
            else:
                _logger.warning(f"[MARKETPLACE] {url} devolvió {resp.status_code}: {resp.text[:200]}")

        if success:
            self.last_sync = fields.Datetime.now()
        else:
            _logger.warning(f"[MARKETPLACE] No se pudo obtener información de {self.name}")

    # ========================================================================
    # PROCESAR DATOS Y CREAR TICKETS EN ODOO
    # ========================================================================
    def _process_conversations(self, data):
        """Crea o actualiza tickets según los datos de Mirakl."""
        Ticket = self.env["marketplace.ticket"]
        count_new = 0
        count_updated = 0

        # Determinar estructura de respuesta
        conversations = []
        if isinstance(data, dict):
            conversations = data.get("conversations") or data.get("messages") or []
        elif isinstance(data, list):
            conversations = data

        for conv in conversations:
            conv_id = str(conv.get("id") or conv.get("conversation_id") or conv.get("message_id"))
            subject = conv.get("subject") or conv.get("topic") or "Mensaje de cliente"
            customer = conv.get("customer") or conv.get("from") or {}
            customer_name = customer.get("name") if isinstance(customer, dict) else str(customer)

            # Verificar si ya existe el ticket
            ticket = Ticket.search([
                ("external_id", "=", conv_id),
                ("account_id", "=", self.id)
            ], limit=1)

            vals = {
                "name": subject,
                "account_id": self.id,
                "external_id": conv_id,
                "customer_name": customer_name or "Cliente",
                "marketplace": self.marketplace or self.name,
                "state": "new",
            }

            if ticket:
                ticket.write(vals)
                count_updated += 1
            else:
                ticket = Ticket.create(vals)
                count_new += 1

            # Intentar sincronizar los mensajes del hilo
            ticket.action_sync_messages()

        _logger.info(f"[MARKETPLACE] {self.name}: {count_new} tickets nuevos, {count_updated} actualizados.")

