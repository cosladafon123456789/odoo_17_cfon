from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"

    whatsapp_sent = fields.Boolean(string="WhatsApp enviado (TCtM)", default=False, help="Marcado cuando se envía el WhatsApp de TeComproTuMovil.")

    @api.model
    def button_validate(self):
        """Tras validar, intenta enviar WhatsApp si procede."""
        res = super(StockPicking, self).button_validate()

        for picking in self:
            purchase = picking.purchase_id
            if not purchase:
                continue

            # Solo procede si el flag de 'Te compro tu móvil' está marcado
            if not purchase.x_studio_comprado:
                continue

            partner = purchase.partner_id
            phone = (partner.phone or partner.mobile or "").strip()
            if not phone:
                _logger.info("TCtM: Pedido %s sin teléfono del comprador; no se envía WhatsApp.", purchase.name)
                continue

            # Evita reenvíos: si ya se envió en este picking o a este número anteriormente con la plantilla
            template = self.env["whatsapp.template"].search([
                ("name", "=", "tecomprotumovil"),
                ("state", "=", "approved"),
            ], limit=1)
            if not template:
                _logger.warning("TCtM: No se encontró plantilla WhatsApp 'tecomprotumovil' en estado 'approved'.")
                continue

            if picking.whatsapp_sent:
                _logger.info("TCtM: Picking %s ya marcado como enviado; no se repite.", picking.name)
                continue

            sent_before = self.env["whatsapp.message"].search_count([
                ("mobile", "=", phone),
                ("template_id", "=", template.id),
                ("state", "in", ["sent", "delivered", "read"])
            ])
            if sent_before:
                _logger.info("TCtM: Ya se envió WhatsApp a %s con esta plantilla previamente; no se repite.", phone)
                picking.whatsapp_sent = True  # reflejar que ya lo tenía
                continue

            try:
                # Crear el mensaje vinculado al pedido de compra
                Message = self.env["whatsapp.message"]
                msg_vals = {
                    "template_id": template.id,
                    "partner_id": partner.id,
                    "mobile": phone,
                    "model": "purchase.order",
                    "res_id": purchase.id,
                }
                message = Message.create(msg_vals)

                # Enviar usando el método disponible en el módulo oficial
                send_done = False
                for method_name in ("action_send", "send_message", "send"):
                    if hasattr(message, method_name):
                        try:
                            getattr(message, method_name)()
                            send_done = True
                            break
                        except Exception as e:
                            _logger.debug("TCtM: fallo en %s(): %s", method_name, e)

                if not send_done:
                    # Fallback: some implementations enqueue messages via sudo on model
                    if hasattr(Message, "send_messages"):
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
                    # Bloquear edición posterior del flag en la compra
                    purchase.write({"x_studio_comprado_readonly": True})
                    _logger.info("TCtM: WhatsApp enviado a %s para %s.", phone, purchase.name)
                else:
                    _logger.warning("TCtM: No se pudo ejecutar el envío del mensaje para %s.", phone)

            except Exception as e:
                _logger.warning("TCtM: Error creando/enviando WhatsApp: %s", e)

        return res