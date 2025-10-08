# -*- coding: utf-8 -*-
from odoo import api, models
import logging, json
import requests
from datetime import datetime, timezone

_logger = logging.getLogger(__name__)

class MiraklClient(models.AbstractModel):
    _name = "mirakl.client"
    _description = "Cliente HTTP para Mirakl (genérico)"

    def _headers(self, account):
        headers = {
            account.header_name or "Authorization": account.api_key or "",
            "Accept": "application/json"
        }
        return headers

    def _base(self, account):
        return (account.api_base or "").rstrip("/")

    def fetch_new_conversations(self, account, updated_since=None, limit=50):
        """
        Intenta primero con API de Conversaciones; si falla, prueba API antigua de Mensajes.
        """
        base = self._base(account)
        params = {}
        if updated_since:
            # formato ISO8601
            if isinstance(updated_since, str):
                params["updated_since"] = updated_since
            else:
                params["updated_since"] = updated_since.astimezone(timezone.utc).isoformat()
        params["max"] = limit
        try_endpoints = [
            account.conv_list_endpoint or "/api/conversations",
            account.legacy_messages_list_endpoint or "/api/messages"
        ]
        for ep in try_endpoints:
            url = f"{base}{ep}"
            try:
                resp = requests.get(url, headers=self._headers(account), params=params, timeout=30)
                if resp.status_code == 200:
                    return ep, resp.json()
                else:
                    _logger.warning("Mirakl fetch %s -> %s %s", url, resp.status_code, resp.text[:200])
            except Exception as e:
                _logger.exception("Mirakl fetch error %s: %s", url, e)
        return None, {}

    def fetch_conversation_messages(self, account, conv_id):
        base = self._base(account)
        try_endpoints = [
            (account.conv_messages_endpoint or "/api/conversations/{id}/messages").replace("{id}", str(conv_id)),
            (account.legacy_messages_thread_endpoint or "/api/messages/{id}").replace("{id}", str(conv_id)),
        ]
        for ep in try_endpoints:
            url = f"{base}{ep}"
            try:
                resp = requests.get(url, headers=self._headers(account), timeout=30)
                if resp.status_code == 200:
                    return ep, resp.json()
                else:
                    _logger.warning("Mirakl fetch conv %s -> %s %s", url, resp.status_code, resp.text[:200])
            except Exception as e:
                _logger.exception("Mirakl fetch conv error %s: %s", url, e)
        return None, {}

    def send_message(self, account, conv_id, body):
        base = self._base(account)
        payload = {"body": body}
        try_endpoints = [
            (account.conv_send_message_endpoint or "/api/conversations/{id}/messages").replace("{id}", str(conv_id)),
            (account.legacy_send_message_endpoint or "/api/messages/{id}/answer").replace("{id}", str(conv_id)),
        ]
        for ep in try_endpoints:
            url = f"{base}{ep}"
            try:
                resp = requests.post(url, headers=self._headers(account), json=payload, timeout=30)
                if resp.status_code in (200,201,202):
                    return True, resp.json() if resp.text else {}
                else:
                    _logger.warning("Mirakl send %s -> %s %s", url, resp.status_code, resp.text[:200])
            except Exception as e:
                _logger.exception("Mirakl send error %s: %s", url, e)
        return False, {}
