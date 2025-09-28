# -*- coding: utf-8 -*-
from odoo import models
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            try:
                template = self.env["whatsapp.template"].search(
                    [("name", "=", "Factura validada")], limit=1
                )
                if not template:
                    _logger.warning("No se encontró la plantilla de WhatsApp 'Factura validada'.")
                    continue

                phone = picking.partner_id.mobile or picking.partner_id.phone
                if not phone:
                    _logger.info("Partner %s no tiene teléfono para WhatsApp.", picking.partner_id.display_name)
                    continue

                if "whatsapp.composer" in self.env:
                    composer = self.env["whatsapp.composer"].create({
                        "res_model": "stock.picking",
                        "res_id": picking.id,
                        "template_id": template.id,
                        "phone": phone,
                    })
                    if hasattr(composer, "action_send_whatsapp_template"):
                        composer.action_send_whatsapp_template()
                        _logger.info("WhatsApp enviado automáticamente a %s para picking %s", phone, picking.name)
                    else:
                        _logger.warning("El modelo whatsapp.composer no tiene método action_send_whatsapp_template.")
                else:
                    _logger.warning("No existe el modelo whatsapp.composer en esta base de datos.")

            except Exception as e:
                _logger.exception("Error enviando WhatsApp automático en picking %s: %s", picking.name, e)
                picking.message_post(body=f"⚠ Error al enviar WhatsApp automático: {e}")
        return res
