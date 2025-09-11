# -*- coding: utf-8 -*-
import logging, re, io, tempfile
from datetime import datetime
from dateutil import parser as dateparser
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

try:
    from pdfminer_high_level import extract_text  # typo guard
except Exception:
    try:
        from pdfminer.high_level import extract_text
    except Exception as e:
        extract_text = None
        _logger.warning("pdfminer not available: %s", e)

try:
    import pytesseract
    from PIL import Image
except Exception as e:
    pytesseract = None
    Image = None
    _logger.info("pytesseract/PIL not available (image OCR disabled): %s", e)


class InvoiceOCREngine(models.Model):
    @api.model
    def cron_process_invoices_folder(self):
        """Procesa automáticamente documentos nuevos en la carpeta OCR.
        Reglas:
        - Solo PDFs/JPG/PNG
        - Solo documentos sin enlace (res_model vacío) para evitar duplicados.
        """
        try:
            folder = self.env.ref("cfon_ocr_final.folder_vendor_bills_ocr_pro", raise_if_not_found=False) or \
                     self.env.ref("cfon_ocr_final_bind.folder_vendor_bills_ocr_pro", raise_if_not_found=False) or \
                     self.env.ref("cfon_ocr_final_auto.folder_vendor_bills_ocr_pro", raise_if_not_found=False)
        except Exception:
            folder = False
        if not folder:
            return

        Doc = self.env["documents.document"].sudo().with_context(active_test=False)
        docs = Doc.search([
            ("folder_id", "=", folder.id),
            ("res_model", "=", False),
            ("mimetype", "in", ["application/pdf", "image/jpeg", "image/png"]),
        ], limit=50, order="id asc")
        for d in docs:
            try:
                self.process_document(d)
            except Exception as e:
                d.message_post(body="OCR: error al procesar: %s" % e)

    _name = "invoice.ocr.engine"
    _description = "Motor OCR gratuito para facturas proveedor"

    @api.model
    def _extract_text_from_pdf(self, bin_content):
        if not extract_text:
            return ""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tf:
            tf.write(bin_content)
            tf.flush()
            try:
                return extract_text(tf.name) or ""
            except Exception as e:
                _logger.exception("Error extracting text from PDF: %s", e)
                return ""

    @api.model
    def _extract_text_from_image(self, bin_content, lang="spa+eng"):
        if not (pytesseract and Image):
            return ""
        try:
            img = Image.open(io.BytesIO(bin_content))
            return pytesseract.image_to_string(img, lang=lang) or ""
        except Exception as e:
            _logger.exception("Error OCR image: %s", e)
            return ""

    CIF_PATTERN = re.compile(r"\b([A-Z]\d{7}[A-Z0-9])\b", re.I)
    IBAN_PATTERN = re.compile(r"\b([A-Z]{2}\d{2}[A-Z0-9]{1,30})\b")
    CURRENCY_PATTERN = re.compile(r"\b(EUR|USD|GBP)\b|([€$£])")

    TOTAL_PATTERNS = [
        re.compile(r"(?i)total\s*(?:a\s*pagar|importe|bruto|factura)?\s*[:\-]?\s*([\d\.,]+)"),
        re.compile(r"(?i)importe\s*total\s*[:\-]?\s*([\d\.,]+)"),
    ]
    NUMBER_PATTERNS = [
        re.compile(r"(?i)(?:factura|invoice|n[ºo]|num(?:ero)?)\s*[:\-]?\s*([A-Z0-9\-\./]+)"),
    ]

    def _normalize_amount(self, val):
        v = val.replace(" ", "").replace("\u00A0", "")
        if "," in v and "." in v and v.rfind(",") > v.rfind("."):
            v = v.replace(".", "").replace(",", ".")
        elif "," in v and "." not in v:
            v = v.replace(",", ".")
        try:
            return float(v)
        except Exception:
            return 0.0

    def _find_first(self, patterns, text):
        for p in patterns:
            m = p.search(text or "")
            if m:
                return m.group(m.lastindex or 1).strip()
        return ""

    def _detect_currency(self, text):
        m = self.CURRENCY_PATTERN.search(text or "")
        if not m:
            return None
        code_or_symbol = m.group(1) or m.group(2)
        Map = {"€": "EUR", "$": "USD", "£": "GBP"}
        return Map.get(code_or_symbol, code_or_symbol)

    def _detect_partner(self, text):
        Partner = self.env["res.partner"]
        m = self.CIF_PATTERN.search(text or "")
        if m:
            vat = m.group(1).upper().replace(" ", "")
            p = Partner.search([("vat","=",vat)], limit=1)
            if p:
                return p
        m = self.IBAN_PATTERN.search(text or "")
        if m:
            iban = m.group(1).replace(" ", "")
            bank = self.env["res.partner.bank"].search([("acc_number","ilike",iban)], limit=1)
            if bank and bank.partner_id:
                return bank.partner_id
        lines = [l.strip() for l in (text or "").splitlines() if l.strip()]
        cand = ""
        for l in lines[:20]:
            if len(l) >= 4 and sum(1 for c in l if c.isupper()) >= max(4, int(0.6*len(l))):
                cand = l
                break
        if cand:
            p = Partner.search([("name","ilike",cand)], limit=1)
            if p:
                return p
        p = Partner.search([("name","=", "Proveedor desconocido (OCR)")], limit=1)
        if not p:
            p = Partner.create({"name":"Proveedor desconocido (OCR)", "supplier_rank":1, "company_type":"company"})
        return p

    @api.model
    def process_document(self, document):
        ICP = self.env["ir.config_parameter"].sudo()
        enable_images = ICP.get_param("cfon_ocr_final.enable_images") == "True"
        lang = ICP.get_param("cfon_ocr_final.language") or "spa"
        currency_fallback_id = int(ICP.get_param("cfon_ocr_final.currency_fallback_id") or 0)
        default_tax_id = int(ICP.get_param("cfon_ocr_final.default_tax_id") or 0)

        if document.mimetype not in ("application/pdf", "image/jpeg", "image/png"):
            document.message_post(body=_("Mimetype no soportado para OCR: %s") % document.mimetype)
            return False
        bin_content = document._get_file_content()[0]
        text = ""
        if document.mimetype == "application/pdf":
            text = self._extract_text_from_pdf(bin_content)
        else:
            if enable_images:
                ocr_lang = "spa+eng" if lang=="spa" else "eng+spa"
                text = self._extract_text_from_image(bin_content, lang=ocr_lang)
        if not text:
            document.message_post(body=_("OCR no pudo extraer texto. PDF con texto o habilitar imágenes + pytesseract."))
            return False

        # Guard DV1
        if "DECLARACIÓN DE DATOS RELATIVOS AL VALOR EN ADUANA" in (text or "") or "D.V.1" in (text or ""):
            document.message_post(body=_("Documento DV1 de aduanas detectado; no se procesa como factura."))
            return False

        ref = self._find_first(self.NUMBER_PATTERNS, text) or document.name
        try:
            inv_date = dateparser.parse(self._find_first([re.compile(r"(\d{2}[/-]\d{2}[/-]\d{4})"),
                                                          re.compile(r"(\d{4}[/-]\d{2}[/-]\d{2})")], text), dayfirst=True).date()
        except Exception:
            inv_date = fields.Date.context_today(self)

        raw_total = self._find_first(self.TOTAL_PATTERNS, text)
        tot = self._normalize_amount(raw_total) if raw_total else 0.0

        cur_code = self._detect_currency(text) or self.env.company.currency_id.name
        Currency = self.env["res.currency"]
        currency = Currency.search([("name","=",cur_code)], limit=1) or self.env.company.currency_id

        partner = self._detect_partner(text)

        invoice_date_due = False
        if partner.property_supplier_payment_term_id:
            try:
                invoice_date_due = partner.property_supplier_payment_term_id.compute(inv_date, currency=currency)[-1][0]
            except Exception:
                invoice_date_due = False

        tax_to_use = self.env["account.tax"].browse(default_tax_id) if default_tax_id else self.env["account.tax"]
        if tax_to_use and not tax_to_use.exists():
            tax_to_use = self.env["account.tax"]

        taxes = [(6,0,[tax_to_use.id])] if getattr(tax_to_use, "id", False) else []

        journal = self.env["account.journal"].search([("type","=","purchase"), ("company_id","=",self.env.company.id)], limit=1)

        move_vals = {
            "move_type": "in_invoice",
            "partner_id": partner.id,
            "invoice_date": inv_date,
            "invoice_date_due": invoice_date_due,
            "ref": ref,
            "currency_id": currency.id,
            "invoice_line_ids": [(0,0,{"name": _("Factura importada por OCR"), "quantity":1.0, "price_unit": tot, "tax_ids": taxes})],
            "journal_id": journal.id if journal else False,
        }
        move = self.env["account.move"].sudo().create(move_vals)

        document.write({"res_model": "account.move", "res_id": move.id})
        document.message_post(body=_("Factura creada por OCR (CFON OCR Final): %s") % move.display_name)
        return move
