# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ocr_default_purchase_journal_id = fields.Many2one("account.journal", string="Diario de compras por defecto",
                                                      domain="[('type', '=', 'purchase')]",
                                                      config_parameter="cfon_ocr_final.default_purchase_journal_id")
    ocr_default_tax_id = fields.Many2one("account.tax", string="Impuesto por defecto",
                                         domain="[('type_tax_use','in',('purchase','none'))]",
                                         config_parameter="cfon_ocr_final.default_tax_id")
    ocr_currency_fallback_id = fields.Many2one("res.currency", string="Divisa por defecto",
                                               config_parameter="cfon_ocr_final.currency_fallback_id")
    ocr_language = fields.Selection([("spa","Español"),("eng","Inglés")], default="spa",
                                    config_parameter="cfon_ocr_final.language")
    ocr_enable_images = fields.Boolean(string="OCR para imágenes (requiere pytesseract)",
                                       config_parameter="cfon_ocr_final.enable_images")
