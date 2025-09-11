# -*- coding: utf-8 -*-
from odoo import models, fields

class InvoiceParserConfig(models.Model):
    _name = "invoice.parser.config"
    _description = "Reglas OCR por proveedor (opcional)"

    name = fields.Char(required=True)
    partner_id = fields.Many2one("res.partner", string="Proveedor")
    regex_date = fields.Char(help="Expresión regular para la fecha")
    regex_due = fields.Char(help="Expresión regular para el vencimiento")
    regex_number = fields.Char(help="Expresión regular para número de factura")
    regex_total = fields.Char(help="Expresión regular para total")
