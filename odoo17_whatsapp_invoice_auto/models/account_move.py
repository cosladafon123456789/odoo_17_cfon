# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

WHATSAPP_GRAPH_VERSION = "v20.0"

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super().action_post()
        # Solo facturas de cliente
        for move in self.filtered(lambda m: m.move_type in ("out_invoice","out_refund")):
            try:
                move._wa_send_invoice_message()
            except Exception as e:
                _logger.exception("Error enviando WhatsApp de factura %s: %s", move.name, e)
        return res

    def _wa_get_account(self):
        """Busca la cuenta de WhatsApp configurada en Odoo 17 (modelo whatsapp.account)."""
        WaAccount = self.env["whatsapp.account"].sudo()
        account = WaAccount.search([], limit=1)
        if not account:
            raise UserError(_("No hay ninguna cuenta de WhatsApp configurada (whatsapp.account)."))
        return account

    def _wa_require_partner_mobile(self, partner):
        number = (partner.mobile or partner.phone or "").replace(" ", "")
        if not number:
            raise UserError(_("El cliente %s no tiene teléfono/móvil configurado.") % (partner.display_name,))
        # Asegurar formato internacional si falta el '+'
        if not number.startswith('+'):
            # No forzamos, pero advertimos en logs
            _logger.warning("Número sin prefijo internacional para %s: %s", partner.display_name, number)
        return number

    def _wa_attachment_public_link(self, attachment):
        """Devuelve un enlace público al adjunto usando access_token estándar de Odoo."""
        # Aseguramos que tiene access_token
        if not attachment.access_token:
            attachment.sudo().generate_access_token()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        return f"{base_url}/web/content/{attachment.id}?download=1&access_token={attachment.access_token}"

    def _wa_render_invoice_pdf_attachment(self):
        """Genera (o encuentra) el PDF de la factura y devuelve el attachment."""
        self.ensure_one()
        report = self.env.ref("account.account_invoices")
        # Render y adjunto
        pdf_content, _ = report._render_qweb_pdf(self.ids)
        filename = (self.name or "Factura").replace("/", "-") + ".pdf"
        Attachment = self.env["ir.attachment"].sudo()
        # Buscar si ya existe
        attach = Attachment.search([("res_model","=",self._name),("res_id","=",self.id),("name","=",filename)], limit=1)
        if not attach:
            attach = Attachment.create({
                "name": filename,
                "type": "binary",
                "datas": self.env['ir.binary'].sudo()._encode_base64(pdf_content),
                "res_model": self._name,
                "res_id": self.id,
                "mimetype": "application/pdf",
            })
        return attach

    def _wa_get_message_template(self, partner, sale_order_name=None):
        ICP = self.env["ir.config_parameter"].sudo()
        template = ICP.get_param("whatsapp_invoice_auto.message_template") or \
            ("Hola {name}, gracias por tu compra {order_name}. "
             "Aquí tienes tu factura {invoice_name}: {invoice_url}")
        return template.format(
            name=partner.name or "",
            order_name=sale_order_name or "",
            invoice_name=self.name or "",
            company_name=self.company_id.name or "",
            invoice_url=self._context.get("wa_invoice_url","")
        ).strip()

    def _wa_send_invoice_message(self):
        self.ensure_one()
        account = self._wa_get_account().sudo()
        partner = self.partner_id
        # 1) Número destino
        to_number = self._wa_require_partner_mobile(partner)

        # 2) Generar PDF y URL pública
        attach = self._wa_render_invoice_pdf_attachment()
        public_url = self._wa_attachment_public_link(attach)
        # Guardamos URL en contexto para render
        ctx = dict(self._context, wa_invoice_url=public_url)

        # 3) Mensaje de texto
        body_text = self.with_context(ctx)._wa_get_message_template(partner, getattr(self.invoice_origin, 'name', self.invoice_origin))

        # 4) Enviar via Cloud API usando las credenciales de whatsapp.account
        phone_number_id = getattr(account, "phone_number_id", None) or getattr(account, "number_id", None)
        access_token = getattr(account, "access_token", None) or getattr(account, "token", None)

        if not phone_number_id or not access_token:
            raise UserError(_("Faltan credenciales en la cuenta de WhatsApp (Phone Number ID / Access Token)."))

        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        base_url = f"https://graph.facebook.com/{WHATSAPP_GRAPH_VERSION}/{phone_number_id}"

        # 4a) Enviar texto
        json_text = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": body_text[:4096]},
        }
        resp1 = requests.post(f"{base_url}/messages", headers=headers, json=json_text, timeout=30)
        if resp1.status_code >= 400:
            _logger.error("Fallo enviando texto WhatsApp: %s %s", resp1.status_code, resp1.text)

        # 4b) Enviar documento por link
        json_doc = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "document",
            "document": {
                "link": public_url,
                "filename": attach.name or "invoice.pdf",
            },
        }
        resp2 = requests.post(f"{base_url}/messages", headers=headers, json=json_doc, timeout=30)
        if resp2.status_code >= 400:
            raise UserError(_("No se pudo enviar el PDF por WhatsApp: %s") % resp2.text)

        _logger.info("WhatsApp enviado a %s para factura %s", to_number, self.name)
        return True