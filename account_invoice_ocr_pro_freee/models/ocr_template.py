# -*- coding: utf-8 -*-
from odoo import models, fields

class InvoiceOCRTemplate(models.Model):
    _name = "invoice.ocr.template"
    _description = "Plantilla OCR por proveedor (regex)"

    name = fields.Char(required=True)
    partner_id = fields.Many2one("res.partner", string="Proveedor")
    active = fields.Boolean(default=True)
    priority = fields.Integer(default=10, help="Menor número = mayor prioridad.")
    language = fields.Selection([("spa","Español"),("eng","Inglés")], default="spa")
    date_format = fields.Char(default="%d/%m/%Y", help="Formato fecha p.ej. %d/%m/%Y")

    regex_invoice_number = fields.Char(string="Regex Nº factura")
    regex_date = fields.Char(string="Regex fecha")
    regex_total = fields.Char(string="Regex total")
    regex_currency = fields.Char(string="Regex divisa")
    regex_vat = fields.Char(string="Regex CIF/NIF proveedor")
    regex_due_date = fields.Char(string="Regex vencimiento")

    line_regex = fields.Text(string="Regex líneas (opcional)",
        help="Una por línea. Cada regex debe tener grupos: descripcion, cantidad, precio_unit, iva_pct opcional.")
