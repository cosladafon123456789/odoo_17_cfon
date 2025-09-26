# -*- coding: utf-8 -*-
from odoo import models, api, _
import logging
import re

_logger = logging.getLogger(__name__)

PHONE_CLEAN_RE = re.compile(r"[^\d+]")

def _normalize_e164(phone: str) -> str:
    if not phone:
        return phone
    phone = PHONE_CLEAN_RE.sub("", phone or "")
    # No intentamos añadir prefijo país automáticamente para evitar errores.
    return phone

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super().button_validate()

        for picking in self:
            try:
                # Solo para entregas a clientes
                if picking.picking_type_id.code != "outgoing":
                    continue
                partner = picking.partner_id or picking.sale_id.partner_id
                if not partner:
                    continue

                icp = self.env['ir.config_parameter'].sudo()
                enabled = icp.get_param('whatsapp_delivery_notify.enabled', 'True') == 'True'
                if not enabled:
                    continue

                # Obtener teléfonos según prioridad configurada
                priority = icp.get_param('whatsapp_delivery_notify.phone_priority', 'mobile,phone')
                phones = []
                for field in [p.strip() for p in priority.split(',') if p.strip()]:
                    val = getattr(partner, field, False)
                    if val:
                        phones.append(val)
                phone = _normalize_e164(phones[0] if phones else partner.mobile or partner.phone)
                if not phone:
                    _logger.info("WhatsApp AutoSend: partner %s sin teléfono.", partner.display_name)
                    continue

                template_name = icp.get_param('whatsapp_delivery_notify.template_name', 'Factura validada')
                lang = icp.get_param('whatsapp_delivery_notify.lang', 'es')

                # Intento 1: Conector genérico configurable
                connector_model = icp.get_param('whatsapp_delivery_notify.connector_model', '')
                connector_method = icp.get_param('whatsapp_delivery_notify.connector_method', 'whatsapp_send_template')
                payload = {
                    'phone': phone,
                    'template_name': template_name,
                    'lang': lang,
                    'partner_id': partner.id,
                    'model': 'stock.picking',
                    'res_id': picking.id,
                    'context': {'origin': 'auto_delivery_validate'},
                }
                if connector_model and connector_model in self.env:
                    connector = self.env[connector_model].sudo()
                    if hasattr(connector, connector_method):
                        _logger.info("WhatsApp AutoSend: usando conector %s.%s -> %s", connector_model, connector_method, payload)
                        try:
                            getattr(connector, connector_method)(**payload)
                            continue  # éxito
                        except Exception as e:
                            _logger.exception("WhatsApp AutoSend: fallo conector %s.%s: %s", connector_model, connector_method, e)

                # Intento 2: Módulo nativo de Odoo 'whatsapp' si está instalado
                if 'whatsapp.template' in self.env:
                    wt = self.env['whatsapp.template'].sudo().search([('name', '=', template_name)], limit=1)
                    if wt:
                        # Varios conectores usan un método 'send_message' o 'send'.
                        # Probamos ambos de manera segura.
                        try:
                            if hasattr(wt, 'send_message'):
                                _logger.info("WhatsApp AutoSend: enviando con whatsapp.template.send_message -> %s", payload)
                                wt.send_message(model='stock.picking', res_id=picking.id, partner_id=partner.id, phone=phone, lang=lang)
                                continue
                            elif hasattr(wt, 'send'):
                                _logger.info("WhatsApp AutoSend: enviando con whatsapp.template.send -> %s", payload)
                                wt.send(model='stock.picking', res_id=picking.id, partner_id=partner.id, phone=phone, lang=lang)
                                continue
                            else:
                                _logger.warning("WhatsApp AutoSend: plantilla encontrada pero sin método público conocido (send_message/send).")
                        except Exception as e:
                            _logger.exception("WhatsApp AutoSend: error enviando con whatsapp.template: %s", e)
                    else:
                        _logger.warning("WhatsApp AutoSend: plantilla '%s' no encontrada en whatsapp.template.", template_name)

                # Si no hay conector ni módulo nativo funcional
                _logger.warning("WhatsApp AutoSend: no se pudo enviar WhatsApp para picking %s (partner %s).", picking.name, partner.display_name)

            except Exception as e:
                _logger.exception("WhatsApp AutoSend: excepción inesperada en picking %s: %s", picking.name, e)

        return res
