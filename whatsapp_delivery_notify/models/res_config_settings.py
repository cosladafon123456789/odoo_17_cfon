# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_autosend_enabled = fields.Boolean(string="Enviar WhatsApp al validar entregas", config_parameter='whatsapp_delivery_notify.enabled', default=True)
    whatsapp_template_name = fields.Char(string="Nombre de plantilla WhatsApp", config_parameter='whatsapp_delivery_notify.template_name', default="Factura validada")
    whatsapp_lang = fields.Char(string="Idioma plantilla (ej. es, es_ES)", config_parameter='whatsapp_delivery_notify.lang', default="es")
    whatsapp_phone_priority = fields.Char(string="Prioridad de campos de teléfono", help="Campos de partner separados por coma en orden de prioridad. Ej: mobile,phone", config_parameter='whatsapp_delivery_notify.phone_priority', default="mobile,phone")
    whatsapp_connector_model = fields.Char(string="Modelo conector (opcional)", help="Si usas un módulo de WhatsApp de tercero, indica aquí el modelo. Ej: whatsapp.connector", config_parameter='whatsapp_delivery_notify.connector_model')
    whatsapp_connector_method = fields.Char(string="Método del conector", help="Método que recibe (phone, template_name, lang, partner_id, model, res_id, context)", config_parameter='whatsapp_delivery_notify.connector_method', default="whatsapp_send_template")
