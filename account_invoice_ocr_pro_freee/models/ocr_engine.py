# -*- coding: utf-8 -*-
import logging, re, io, tempfile
from datetime import datetime
from dateutil import parser as dateparser
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

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
    EU_VAT_PREFIXES = {
        "AT","BE","BG","CY","CZ","DE","DK","EE","IE","EL","ES","FI","FR","HR","HU","IT","LT","LU","LV","MT","NL","PL","PT","RO","SE","SI","SK"
    }

    def _auto_fiscal_position(self, partner, company, text=None):
        """
        Try to pick Odoo's *native* fiscal position using existing rules:
        - Prefer account.fiscal.position with auto_apply and matching country/country_group & vat_required.
        - Fallback to _get_fiscal_position (Odoo's internal resolver) if available.
        Returns a fiscal position record or False.
        """
        FP = self.env["account.fiscal.position"].with_company(company).sudo()
        vat = (partner.vat or "").upper().replace(" ","")
        # If EU B2B (non-ES) and company is ES
        if vat and len(vat) >= 2:
            prefix = vat[:2]
        else:
            prefix = ""
        try:
            company_country = company.country_id.code or ""
        except Exception:
            company_country = ""
        # 1) Use auto-apply rules if any
        domain = [("auto_apply","=",True)]
        # If supplier is EU non-ES and company ES, try EU + VAT-required mappings
        if prefix and prefix in self.EU_VAT_PREFIXES and prefix != company_country:
            domain += ["|", ("country_group_id.name","ilike","European Union"), ("country_id", "=", False)]
        fps = FP.search(domain, order="sequence asc, id asc")
        for fp in fps:
            # Basic checks: require VAT if template/rules need it
            if getattr(fp, "vat_required", False):
                if not vat:
                    continue
            # If fp has country set, ensure it matches supplier or is empty
            if fp.country_id and partner.country_id and fp.country_id != partner.country_id:
                continue
            return fp
        # 2) Fallback to Odoo's resolver if present
        resolver = getattr(FP, "_get_fiscal_position", None) or getattr(FP, "get_fiscal_position", None)
        if resolver:
            try:
                return resolver(partner, delivery_partner=partner)
            except TypeError:
                try:
                    return resolver(partner)
                except Exception:
                    return self.env["account.fiscal.position"]
        return self.env["account.fiscal.position"]

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

    def _apply_template(self, text):
        T = self.env["invoice.ocr.template"].search([("active","=",True)], order="priority asc, id asc")
        for t in T:
            if t.partner_id:
                if t.regex_vat:
                    m = re.search(t.regex_vat, text or "", re.I|re.M)
                    if not m:
                        continue
                else:
                    if t.partner_id.name and t.partner_id.name.lower() not in (text or "").lower():
                        continue
            vals = {}
            if t.regex_invoice_number:
                m = re.search(t.regex_invoice_number, text or "", re.I|re.M)
                if m: vals["ref"] = (m.group(m.lastindex or 1)).strip()
            if t.regex_date:
                m = re.search(t.regex_date, text or "", re.I|re.M)
                if m:
                    raw = (m.group(m.lastindex or 1)).strip()
                    try:
                        if t.date_format:
                            vals["invoice_date"] = datetime.strptime(raw, t.date_format).date()
                        else:
                            vals["invoice_date"] = dateparser.parse(raw, dayfirst=True).date()
                    except Exception:
                        pass
            if t.regex_total:
                m = re.search(t.regex_total, text or "", re.I|re.M)
                if m:
                    vals["total"] = self._normalize_amount(m.group(m.lastindex or 1))
            if t.regex_currency:
                m = re.search(t.regex_currency, text or "", re.I|re.M)
                if m:
                    cur = (m.group(m.lastindex or 1)).strip().upper()
                    if cur in ("EUR","USD","GBP"):
                        vals["currency"] = cur
                    elif cur in ("€","$","£"):
                        vals["currency"] = {"€":"EUR","$":"USD","£":"GBP"}[cur]
            if t.regex_due_date:
                m = re.search(t.regex_due_date, text or "", re.I|re.M)
                if m:
                    raw = (m.group(m.lastindex or 1)).strip()
                    try:
                        vals["invoice_date_due"] = dateparser.parse(raw, dayfirst=True).date()
                    except Exception:
                        pass
            lines_vals = []
            if t.line_regex:
                for rx in [r for r in t.line_regex.splitlines() if r.strip()]:
                    for m in re.finditer(rx, text or "", re.I|re.M):
                        gd = m.groups()
                        if not gd:
                            continue
                        desc = gd[0].strip() if len(gd)>=1 else _("Línea OCR")
                        qty = gd[1].strip() if len(gd)>=2 else "1"
                        price = gd[2].strip() if len(gd)>=3 else "0"
                        iva = gd[3].strip() if len(gd)>=4 else ""
                        def norm(x):
                            x = x.replace(" ", "")
                            if "," in x and "." in x and x.rfind(",") > x.rfind("."):
                                x = x.replace(".","").replace(",",".")
                            elif "," in x and "." not in x:
                                x = x.replace(",",".")
                            return x
                        try:
                            qtyf = float(norm(qty))
                        except Exception:
                            qtyf = 1.0
                        try:
                            pricef = float(norm(price))
                        except Exception:
                            pricef = 0.0
                        iva_pct = None
                        try:
                            iva_pct = float(norm(iva)) if iva else None
                        except Exception:
                            iva_pct = None
                        lines_vals.append({"name":desc, "quantity":qtyf, "price_unit":pricef, "iva_pct":iva_pct})
            if vals or lines_vals:
                return vals, lines_vals
        return {}, []

    @api.model
    def process_document(self, document):
        ICP = self.env["ir.config_parameter"].sudo()
        enable_images = ICP.get_param("account_invoice_ocr_pro_free.enable_images") == "True"
        lang = ICP.get_param("account_invoice_ocr_pro_free.language") or "spa"
        currency_fallback_id = int(ICP.get_param("account_invoice_ocr_pro_free.currency_fallback_id") or 0)
        default_tax_id = int(ICP.get_param("account_invoice_ocr_pro_free.default_tax_id") or 0)

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
            document.message_post(body=_("OCR no pudo extraer texto. Se requiere PDF con texto o habilitar imágenes + pytesseract."))
            return False

        # Skip customs DV1 forms
        if "DECLARACIÓN DE DATOS RELATIVOS AL VALOR EN ADUANA" in (text or "") or "D.V.1" in (text or ""):
            document.message_post(body=_("Documento DV1 de aduanas detectado; no se procesa como factura."))
            return False

        t_vals, t_lines = self._apply_template(text)

        ref = t_vals.get("ref") or self._find_first(self.NUMBER_PATTERNS, text) or document.name
        try:
            inv_date = t_vals.get("invoice_date")
            if not inv_date:
                inv_date = dateparser.parse(self._find_first([re.compile(r"(\d{2}[/-]\d{2}[/-]\d{4})"),
                                                              re.compile(r"(\d{4}[/-]\d{2}[/-]\d{2})")], text), dayfirst=True).date()
        except Exception:
            inv_date = fields.Date.context_today(self)

        tot = t_vals.get("total")
        if tot is None:
            raw = self._find_first(self.TOTAL_PATTERNS, text)
            tot = self._normalize_amount(raw) if raw else 0.0

        cur_code = t_vals.get("currency") or self._detect_currency(text)
        Currency = self.env["res.currency"]
        if cur_code:
            currency = Currency.search([("name","=",cur_code)], limit=1)
        else:
            currency = currency_fallback_id and Currency.browse(currency_fallback_id) or self.env.company.currency_id

        partner = self._detect_partner(text)

        invoice_date_due = t_vals.get("invoice_date_due")
        if not invoice_date_due and partner.property_supplier_payment_term_id:
            invoice_date_due = partner.property_supplier_payment_term_id.compute(inv_date, currency=currency)[-1][0]

        tax_to_use = self.env["account.tax"].browse(default_tax_id) if default_tax_id else self.env["account.tax"]
        if tax_to_use and not tax_to_use.exists():
            tax_to_use = self.env["account.tax"]

        line_vals = []
        if t_lines:
            for l in t_lines:
                taxes = []
                if l.get("iva_pct") is not None:
                    tax = self.env["account.tax"].search([("amount","=", l["iva_pct"]), ("type_tax_use","in",["purchase","none"])], limit=1)
                    if tax:
                        taxes = [(6,0,[tax.id])]
                elif getattr(tax_to_use, "id", False):
                    taxes = [(6,0,[tax_to_use.id])]
                line_vals.append((0,0,{
                    "name": l.get("name") or _("Línea OCR"),
                    "quantity": l.get("quantity") or 1.0,
                    "price_unit": l.get("price_unit") or 0.0,
                    "tax_ids": taxes,
                }))
        else:
            taxes = [(6,0,[tax_to_use.id])] if getattr(tax_to_use, "id", False) else []
            line_vals = [(0,0,{
                "name": _("Factura importada por OCR"),
                "quantity": 1.0,
                "price_unit": tot if tot>0 else 0.0,
                "tax_ids": taxes,
            })]

        journal = self.env["account.journal"].search([("type","=","purchase"), ("company_id","=",self.env.company.id)], limit=1)

        move_vals = {
            "move_type": "in_invoice",
            "partner_id": partner.id,
            "invoice_date": inv_date,
            "invoice_date_due": invoice_date_due,
            "ref": ref,
            "currency_id": currency.id,
            "invoice_line_ids": line_vals,
            "journal_id": journal.id if journal else False,
        }
        move = self.env["account.move"].sudo().create(move_vals)

        document.write({
            "res_model": "account.move",
            "res_id": move.id,
        })
        document.message_post(body=_("Factura creada por OCR gratis (Pro): %s") % move.display_name)
        return move
