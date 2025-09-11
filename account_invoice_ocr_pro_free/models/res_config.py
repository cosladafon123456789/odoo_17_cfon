# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ocr_default_purchase_journal_id = fields.Many2one("account.journal", string="Diario de compras por defecto",
                                                      domain="[('type', '=', 'purchase')]",
                                                      config_parameter="account_invoice_ocr_pro_free.default_purchase_journal_id")
    ocr_default_tax_id = fields.Many2one("account.tax", string="Impuesto por defecto",
                                         domain="[('type_tax_use','in',('purchase','none'))]",
                                         config_parameter="account_invoice_ocr_pro_free.default_tax_id")
    ocr_currency_fallback_id = fields.Many2one("res.currency", string="Divisa por defecto",
                                               config_parameter="account_invoice_ocr_pro_free.currency_fallback_id")
    ocr_language = fields.Selection([("spa","Español"),("eng","Inglés")], default="spa",
                                    config_parameter="account_invoice_ocr_pro_free.language")
    ocr_enable_images = fields.Boolean(string="OCR para imágenes (requiere pytesseract)",
                                       config_parameter="account_invoice_ocr_pro_free.enable_images")
