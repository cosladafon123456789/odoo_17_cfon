# -*- coding: utf-8 -*-
from odoo import api, fields, models

class MarketplaceAccount(models.Model):
    _name = "marketplace.account"
    _description = "Cuenta de Marketplace (Mirakl)"
    _rec_name = "name"

    name = fields.Char(required=True)
    marketplace = fields.Selection([
        ("mediamarkt","MediaMarkt"),
        ("pccomponentes","PCComponentes"),
        ("carrefour","Carrefour"),
        ("phonehouse","Phone House"),
        ("otros","Otros"),
    ], string="Marketplace")
    api_base = fields.Char(string="URL base API", required=True, help="Ej: https://marketplace.mediamarkt.es/api")
    api_key = fields.Char(string="API Key", required=True)
    header_name = fields.Char(string="Nombre de cabecera", default="Authorization",
                              help="Algunas instancias Mirakl usan X-API-Key o X-Mirakl-API-Key")

    # Endpoints configurables (por diferencias entre operadores)
    conv_list_endpoint = fields.Char(string="Endpoint listar conversaciones", default="/api/conversations")
    conv_messages_endpoint = fields.Char(string="Endpoint mensajes de conversación", default="/api/conversations/{id}/messages")
    conv_send_message_endpoint = fields.Char(string="Endpoint enviar mensaje", default="/api/conversations/{id}/messages")

    legacy_messages_list_endpoint = fields.Char(string="Endpoint legacy listar mensajes", default="/api/messages")
    legacy_messages_thread_endpoint = fields.Char(string="Endpoint legacy hilo", default="/api/messages/{id}")
    legacy_send_message_endpoint = fields.Char(string="Endpoint legacy responder", default="/api/messages/{id}/answer")

    last_sync = fields.Datetime(string="Última sincronización")

    active = fields.Boolean(default=True)
