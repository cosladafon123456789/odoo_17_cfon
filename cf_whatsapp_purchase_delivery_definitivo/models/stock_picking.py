
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
        """Envía la plantilla 'tecomprotumovil' al partner mediante el módulo oficial WhatsApp de Odoo.

        Esta función intenta utilizar los modelos estándar de Odoo 17:
         - whatsapp.template
         - whatsapp.message

        Si no encuentra la plantilla o no puede enviar, lanza UserError para dejar traza en logs.
        """
        Template = self.env["whatsapp.template"].sudo()
        template = Template.search([("name", "=", "tecomprotumovil")], limit=1)
        if not template:
            raise UserError(_("No se encontró la plantilla de WhatsApp llamada 'tecomprotumovil'."))
        if not template:
            raise UserError(_("No se encontró la plantilla de WhatsApp aprobada llamada 'tecomprotumovil'."))

        phone = self._cf_get_partner_phone(partner)
        if not phone:
            raise UserError(_("El contacto %s no tiene teléfono o móvil establecido.") % (partner.display_name))

        # Crear mensaje WhatsApp usando plantilla
        # API estándar en Odoo 17: el envío se hace creando whatsapp.message con template_id y partner, 
        # y luego llamando a action_send() / _send_messages().
        WMessage = self.env["whatsapp.message"].sudo()
        msg_vals = {
            "template_id": template.id,
            "partner_id": partner.id,
            "number": phone,
            "res_model": self._name,
            "res_id": self.id,
        }
        message = WMessage.create(msg_vals)
        # Intentar enviar
        send_method = getattr(message, "action_send", None) or getattr(message, "_send_messages", None)
        if not send_method:
            # Fallback: algunos despliegues usan método 'send_now'
            send_method = getattr(message, "send_now", None)
        if not send_method:
            raise UserError(_("No se ha podido localizar un método de envío en whatsapp.message (action_send/_send_messages)."))
        send_method()
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
