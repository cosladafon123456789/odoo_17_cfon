# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import tempfile, re, logging
_logger = logging.getLogger(__name__)

try:
    from pdfminer.high_level import extract_text as pdf_extract_text
except Exception:  # pragma: no cover
    pdf_extract_text = None

CIF_RE = re.compile(r'\b([A-Z]\d{7}[A-Z0-9]|[0-9]{8}[A-Z])\b')  # muy básico NIF/CIF

class BillOcrUploadWizard(models.TransientModel):
    _name = "bill.ocr.upload.wizard"
    _description = "Subir con OCR (Facturas Proveedor)"

    attachment_ids = fields.Many2many("ir.attachment", string="PDFs", help="Arrastra aquí tus facturas en PDF.", required=True)
    journal_id = fields.Many2one("account.journal", string="Diario", domain=[("type","=","purchase")], required=True)
    partner_id = fields.Many2one("res.partner", string="Proveedor por defecto")
    set_due_from_text = fields.Boolean(string="Leer vencimiento del PDF", default=True)
    create_one_line_if_no_items = fields.Boolean(string="Crear una línea si no se detectan líneas", default=True)

    def _extract_text(self, bin_data):
        if not pdf_extract_text:
            raise UserError(_("Falta la librería 'pdfminer.six' en el servidor de Odoo."))
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as f:
            f.write(bin_data)
            f.flush()
            text = pdf_extract_text(f.name) or ""
        return text

    def _find_partner(self, text):
        # 1) por CIF/NIF
        match = CIF_RE.search(text.replace(" ", "").upper())
        if match:
            vat = match.group(1)
            partner = self.env["res.partner"].search([("vat","ilike", vat)], limit=1)
            if partner:
                return partner
        # 2) por nombre (muy simple; coger palabras en mayúsculas largas)
        words = re.findall(r'\b[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s&]{5,}\b', text)
        for w in words[:3]:
            partner = self.env["res.partner"].search([("name","ilike", w.strip())], limit=1)
            if partner:
                return partner
        return self.partner_id

    def _parse_amounts(self, text):
        # busca totales comunes: "Base imponible", "IVA", "Total", etc.
        clean = text.replace(".", "").replace(",", ".")
        total = None
        untaxed = None
        tax = None

        for label in ["TOTAL FACTURA", "TOTAL A PAGAR", "TOTAL", "IMPORTE TOTAL"]:
            m = re.search(label + r".{0,30}?([\d]+(?:\.\d{1,2})?)", clean, re.IGNORECASE)
            if m:
                try:
                    total = float(m.group(1))
                    break
                except Exception:
                    pass

        for label in ["BASE IMPONIBLE", "SUBTOTAL"]:
            m = re.search(label + r".{0,30}?([\d]+(?:\.\d{1,2})?)", clean, re.IGNORECASE)
            if m:
                try:
                    untaxed = float(m.group(1))
                    break
                except Exception:
                    pass

        for label in ["IVA", "IMPUESTO", "TAX"]:
            m = re.search(label + r".{0,30}?([\d]+(?:\.\d{1,2})?)", clean, re.IGNORECASE)
            if m:
                try:
                    tax = float(m.group(1))
                    break
                except Exception:
                    pass

        if total is None and untaxed is not None and tax is not None:
            total = untaxed + tax
        if untaxed is None and total is not None and tax is not None:
            untaxed = total - tax
        return untaxed, tax, total

    def _parse_dates_and_number(self, text):
        # fechas en formatos dd/mm/yyyy o dd-mm-yyyy
        date = None
        due = None
        num = None
        m = re.search(r'Fecha\s*(?:de\s*la\s*factura)?\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text, re.IGNORECASE)
        if m: date = fields.Date.from_string(self._normalize_date(m.group(1)))
        m = re.search(r'Vencim(?:iento)?\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text, re.IGNORECASE)
        if m: due = fields.Date.from_string(self._normalize_date(m.group(1)))
        # número
        m = re.search(r'(?:Factura|N[úu]mero|Nº|Num\.?)\s*[:\-]?\s*([A-Za-z0-9/\-]+)', text, re.IGNORECASE)
        if m: num = m.group(1).strip()
        return date, due, num

    def _normalize_date(self, s):
        parts = re.split(r'[/-]', s)
        if len(parts[2]) == 2:
            parts[2] = '20' + parts[2]
        # assume dd/mm/yyyy
        return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"

    def action_process(self):
        self.ensure_one()
        AccountMove = self.env["account.move"]
        created = self.env["account.move"]
        for att in self.attachment_ids:
            if att.mimetype not in ("application/pdf",) and not (att.name or "").lower().endswith(".pdf"):
                raise UserError(_("Solo PDFs. '%s' no es PDF.") % (att.name,))
            bin_data = att._file_read(att.datas)[0] if hasattr(att, "_file_read") else att.datas
            if isinstance(bin_data, str):
                import base64
                bin_data = base64.b64decode(bin_data)
            text = self._extract_text(bin_data)
            partner = self._find_partner(text) or self.partner_id
            if not partner:
                raise UserError(_("No se pudo identificar el proveedor. Selecciona uno por defecto o añade CIF/NIF al partner."))
            inv_date, due_date, supplier_num = self._parse_dates_and_number(text)
            untaxed, tax, total = self._parse_amounts(text)

            move_vals = {
                "move_type": "in_invoice",
                "partner_id": partner.id,
                "invoice_date": inv_date or fields.Date.context_today(self),
                "invoice_payment_term_id": False,
                "invoice_date_due": due_date if self.set_due_from_text else False,
                "invoice_origin": "OCR Upload",
                "ref": supplier_num,
                "journal_id": self.journal_id.id,
                "invoice_line_ids": [],
            }
            # Lines: simple fallback
            if self.create_one_line_if_no_items:
                price = untaxed or total or 0.0
                move_vals["invoice_line_ids"].append((0, 0, {
                    "name": supplier_num or att.name,
                    "quantity": 1.0,
                    "price_unit": price,
                    "tax_ids": [],  # dejar que Odoo calcule impuestos por diario/partner o edítalos luego
                }))

            move = AccountMove.create(move_vals)
            # adjuntar PDF
            att.copy({
                "res_model": "account.move",
                "res_id": move.id,
            })
            created |= move

        action = self.env.ref("account.action_move_in_invoice_type").read()[0]
        action["domain"] = [("id", "in", created.ids)]
        return action
