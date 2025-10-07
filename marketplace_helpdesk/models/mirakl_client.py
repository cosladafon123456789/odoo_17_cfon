import logging
import json
from datetime import timezone
import requests

from odoo import fields, models

_logger = logging.getLogger(__name__)

class MiraklClient(models.AbstractModel):
    _name = "mirakl.client"
    _description = "Cliente Mirakl"

    def _headers(self, account):
        return {
            "Authorization": account.api_key or "",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _get(self, account, path, params=None):
        base = account._normalized_base()
        url = f"{base}/api{path}"
        resp = requests.get(url, headers=self._headers(account), params=params or {}, timeout=30)
        try:
            body = resp.json()
        except Exception:
            _logger.warning("Mirakl fetch %s -> %s %s", url, resp.status_code, resp.text[:400])
            raise
        if resp.status_code >= 300:
            _logger.warning("Mirakl fetch %s -> %s %s", url, resp.status_code, json.dumps(body)[:400])
        return resp.status_code, body

    def test_connection(self, account):
        try:
            code, _ = self._get(account, "/inbox/threads", params={"updated_since": fields.Datetime.now().isoformat()})
            return (code < 400), f"HTTP {code}"
        except Exception as e:
            return False, str(e)

    def fetch_threads(self, account, updated_since=None, unread_only=True, with_messages=False):
        params = {}
        if updated_since:
            if isinstance(updated_since, str):
                params["updated_since"] = updated_since
            else:
                params["updated_since"] = updated_since.astimezone(timezone.utc).isoformat()
        if with_messages:
            params["with_messages"] = "true"
        code, data = self._get(account, "/inbox/threads", params=params)
        if code >= 400:
            return []
        threads = data if isinstance(data, list) else data.get("threads") or data.get("data") or []
        results = []
        for th in threads:
            unread_count = th.get("unread_count") or th.get("unreadCount") or 0
            if unread_only and unread_count <= 0:
                continue
            results.append(th)
        return results

    def fetch_thread_messages(self, account, thread_id):
        code, data = self._get(account, f"/messages", params={"thread_id": thread_id})
        if code >= 400:
            return []
        msgs = data if isinstance(data, list) else data.get("messages") or data.get("data") or []
        return msgs
