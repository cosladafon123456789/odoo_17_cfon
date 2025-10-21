
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    cf_whatsapp_sent = fields.Boolean(
        string="WhatsApp enviado (CF)",
        help="Marcado automáticamente cuando se envía la plantilla TeComproTuMovil para esta entrega."
    )

    def _cf_get_partner_phone(self, partner):
        """Obtiene el teléfono priorizando partner.mobile y luego partner.phone."""
        number = partner.mobile or partner.phone or False
        # Limpieza básica de espacios
        if number:
            number = number.strip()
        return number

    def _cf_send_whatsapp_tecomprotumovil(self, partner):
        """Envía la plantilla 'tecomprotumovil' al número de móvil del partner usando el campo wa_template_id."""
        phone = partner.mobile or partner.phone
        if not phone:
            raise UserError(_("El contacto %s no tiene teléfono o móvil configurado.") % partner.display_name)

        Template = self.env["whatsapp.template"].sudo()
        template = Template.search([("name", "=", "tecomprotumovil")], limit=1)
        if not template:
            raise UserError(_("No se encontró la plantilla de WhatsApp llamada 'tecomprotumovil'."))

        WMessage = self.env["whatsapp.message"].sudo()
        msg_vals = {
            "wa_template_id": template.id,
            "mobile_number": phone,
        }

        # Crear el mensaje
        message = WMessage.create(msg_vals)

        # Usar el método correcto para enviar el mensaje
        if hasattr(message, "action_send_whatsapp_template"):
            message.action_send_whatsapp_template()
        else:
            raise UserError(_("No se encontró el método para enviar el mensaje de WhatsApp."))

        return True

    @api.model
    def _cf_should_send_for_picking(self, picking):
        """Condición: Entrega de compra (incoming) con pedido de compra marcado x_studio_comprado,
        y que no se haya enviado antes ni en el partner ni en la propia entrega.
        """
        if picking.picking_type_id.code != "incoming":
            return False
        po = picking.purchase_id
        if not po:
            return False
        # Campo booleano del usuario en purchase.order
        comprado = bool(getattr(po, "x_studio_comprado", False))
        if not comprado:
            return False
        partner = po.partner_id or picking.partner_id
        if not partner:
            return False
        if picking.cf_whatsapp_sent:
            return False
        if getattr(partner, "cf_whatsapp_tecomprotumovil_sent", False):
            return False
        return True

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for picking in self:
            try:
                if self._cf_should_send_for_picking(picking):
                    partner = picking.purchase_id.partner_id or picking.partner_id
                    picking._cf_send_whatsapp_tecomprotumovil(partner)
                    # Marcar flags para evitar reenvíos
                    picking.cf_whatsapp_sent = True
                    partner.cf_whatsapp_tecomprotumovil_sent = True
            except Exception as e:
                # No impedir la validación, pero dejar registro en chatter
                picking.message_post(
                    body=_("⚠️ No se pudo enviar el WhatsApp TeComproTuMovil automáticamente.<br/>Detalle: %s") % (str(e))
                )
        return res
