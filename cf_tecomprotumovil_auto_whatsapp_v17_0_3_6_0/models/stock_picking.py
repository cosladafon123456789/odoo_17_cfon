from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"

    whatsapp_sent = fields.Boolean(string="WhatsApp enviado (TCtM)", default=False,
                                   help="Marcado cuando se envía el WhatsApp de TeComproTuMovil para este traslado.")

    def button_validate(self):
        res = super().button_validate()

        for picking in self:
            purchase = picking.purchase_id
            if not purchase or not getattr(purchase, "x_studio_comprado", False):
                continue

            # Contacto y teléfono
            partner = picking.partner_id or purchase.partner_id
            phone = (partner.phone or partner.mobile or "").strip()
            if not phone:
                _logger.info("TCtM: Picking %s sin teléfono; no se envía WhatsApp.", picking.name)
                continue

            # Plantilla (aplica a Traslado)
            Template = self.env["whatsapp.template"]
            template = Template.search([("template_name", "=", "tecomprotumovil")], limit=1)                        or Template.search([("name", "=", "tecomprotumovil")], limit=1)
            if not template:
                _logger.warning("TCtM: No se encontró plantilla WhatsApp 'tecomprotumovil'.")
                continue

            if picking.whatsapp_sent:
                _logger.info("TCtM: Picking %s ya marcado como enviado; no se repite.", picking.name)
                continue

            Message = self.env["whatsapp.message"]

            # Evitar duplicado por número y plantilla
            try:
                sent_before = Message.search_count([
                    ("mobile_number", "=", phone),
                    ("wa_template_id", "=", template.id),
                    ("state", "in", ["sent", "delivered", "read"]),
                ])
            except Exception:
                sent_before = Message.search_count([
                    ("mobile_number", "=", phone),
                    ("wa_template_id", "=", template.id),
                ])

            if sent_before:
                picking.whatsapp_sent = True
                # Bloquear flag en compra igualmente
                purchase.write({"x_studio_comprado_readonly": True})
                _logger.info("TCtM: Ya existía un envío previo a %s con esta plantilla; no se repite.", phone)
                continue

            try:
                # Crear (opcional) un mensaje de correo para trazar conversación en el chatter del picking
                mail_message = picking.message_post(body=_("Mensaje automático de WhatsApp programado (TeComproTuMovil)."))

                vals = {
                    "wa_template_id": template.id,
                    "mobile_number": phone,
                    "mail_message_id": mail_message.id if mail_message else False,
                }
                message = Message.create(vals)

                # Intentar enviar con el método existente
                sent = False
                for m in ("action_send", "send_message", "send"):
                    if hasattr(message, m):
                        try:
                            getattr(message, m)()
                            sent = True
                            break
                        except Exception as e:
                            _logger.debug("TCtM: error en %s(): %s", m, e)

                if not sent and hasattr(Message, "send_messages"):
                    try:
                        Message.send_messages()
                        sent = True
                    except Exception as e:
                        _logger.debug("TCtM: error en send_messages(): %s", e)

                if sent:
                    picking.whatsapp_sent = True
                    picking.message_post(body=_("📩 WhatsApp 'TeComproTuMovil' enviado a %s") % phone)
                    # bloquear en la compra
                    purchase.write({"x_studio_comprado_readonly": True})
                else:
                    _logger.warning("TCtM: No se pudo ejecutar el envío del WhatsApp para %s.", phone)

            except Exception as e:
                _logger.warning("TCtM: Error creando/enviando WhatsApp: %s", e)

        return res