from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"

    whatsapp_sent = fields.Boolean(string="WhatsApp enviado (TCtM)", default=False)

    def button_validate(self):
        res = super().button_validate()

        for picking in self:
            purchase = picking.purchase_id
            if not purchase:
                continue

            if not getattr(purchase, "x_studio_comprado", False):
                continue

            partner = purchase.partner_id
            phone = (partner.phone or partner.mobile or "").strip()
            if not phone:
                _logger.info("TCtM: Pedido %s sin teléfono del comprador; no se envía WhatsApp.", purchase.name)
                continue

            template = self.env["whatsapp.template"].search([("template_name", "=", "tecomprotumovil")], limit=1)
            if not template:
                template = self.env["whatsapp.template"].search([("name", "=", "tecomprotumovil")], limit=1)
            if not template:
                _logger.warning("TCtM: No se encontró plantilla WhatsApp 'tecomprotumovil'.")
                continue

            if picking.whatsapp_sent:
                _logger.info("TCtM: Picking %s ya marcado como enviado; no se repite.", picking.name)
                continue

            Message = self.env["whatsapp.message"]
            domain = [("mobile_number", "=", phone), ("wa_template_id", "=", template.id)]
            try:
                sent_before = Message.search_count(domain)
            except Exception:
                sent_before = 0

            if sent_before:
                _logger.info("TCtM: Ya se envió WhatsApp a %s con esta plantilla previamente; no se repite.", phone)
                picking.whatsapp_sent = True
                purchase.write({"x_studio_comprado_readonly": True})
                continue

            try:
                msg_vals = {
                    "wa_template_id": template.id,
                    "mobile_number": phone,
                    "display_name": "TCtM Auto",
                }
                message = Message.create(msg_vals)

                send_done = False
                for method_name in ("action_send", "send_message", "send"):
                    if hasattr(message, method_name):
                        try:
                            getattr(message, method_name)()
                            send_done = True
                            break
                        except Exception as e:
                            _logger.debug("TCtM: fallo en %s(): %s", method_name, e)

                if not send_done and hasattr(Message, "send_messages"):
                    try:
                        Message.send_messages()
                        send_done = True
                    except Exception as e:
                        _logger.debug("TCtM: fallo en send_messages(): %s", e)

                if send_done:
                    picking.whatsapp_sent = True
                    purchase.message_post(
                        body=_("📩 Mensaje de WhatsApp <b>'TeComproTuMovil'</b> enviado a %s") % phone
                    )
                    purchase.write({"x_studio_comprado_readonly": True})
                    _logger.info("TCtM: WhatsApp enviado a %s para %s.", phone, purchase.name)
                else:
                    _logger.warning("TCtM: No se pudo ejecutar el envío del mensaje para %s.", phone)

            except Exception as e:
                _logger.warning("TCtM: Error creando/enviando WhatsApp: %s", e)

        return res