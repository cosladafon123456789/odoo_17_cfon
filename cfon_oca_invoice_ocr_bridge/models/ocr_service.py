
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging, re, io

_logger = logging.getLogger(__name__)

def _to_float(x):
    if not x:
        return 0.0
    s = x.replace(' ', '').replace('€','')
    if s.count(',')==1 and s.count('.')>=1 and s.rfind(',') > s.rfind('.'):
        s = s.replace('.', '').replace(',', '.')
    elif s.count(',')==1 and s.count('.')==0:
        s = s.replace(',', '.')
    import re as _re
    try:
        return float(_re.sub(r'[^0-9\.\-]', '', s))
    except Exception:
        return 0.0

def parse_text_simple(txt):
    import re as _re
    from dateutil import parser as dtparser
    def _find_first(pattern):
        m = _re.search(pattern, txt, _re.IGNORECASE|_re.MULTILINE|_re.DOTALL)
        return m.group(1).strip() if m else None
    data = {}
    data['vat'] = _find_first(r'(?:NIF|CIF|VAT|N.?º\s*IVA)\s*[:\-]?\s*([A-Z0-9\-\.\s]+)')
    data['partner_name'] = _find_first(r'^(?:Proveedor|Vendedor|Seller|Empresa)\s*[:\-]?\s*(.+)$') or _find_first(r'^(.+?)\s*(?:S\.L\.|SL|S\.A\.|SA)\b')
    data['number'] = _find_first(r'(?:Nº\s*Factura|Factura Nº|Invoice No\.?|Invoice #)\s*[:\-]?\s*([A-Z0-9\-/]+)')
    date_raw = _find_first(r'(?:Fecha\s*[:\-]?|Date\s*[:\-]?)\s*([0-9]{1,2}[\-\/\.][0-9]{1,2}[\-\/\.][0-9]{2,4})') or _find_first(r'(\d{4}[\-\/\.]\d{1,2}[\-\/\.]\d{1,2})')
    if date_raw:
        try:
            data['date'] = dtparser.parse(date_raw, dayfirst=True).date().isoformat()
        except Exception:
            data['date'] = None
    data['currency'] = _find_first(r'(?:Moneda|Currency)\s*[:\-]?\s*([A-Z]{3})') or ('EUR' if '€' in txt else None)
    total = _find_first(r'(?:Total\s*Factura|Importe\s*Total|Total\s*Amount)\s*[:\-]?\s*([0-9\.,]+)') or _find_first(r'\bTOTAL\b.*?([0-9\.,]+)')
    total_tax = _find_first(r'(?:IVA|VAT).*?([0-9\.,]+)\s*(?:€|EUR)?')
    untaxed = _find_first(r'(?:Base\s*Imponible|Subtotal|Untaxed)\s*[:\-]?\s*([0-9\.,]+)')
    data['total'] = _to_float(total)
    data['tax_amount'] = _to_float(total_tax)
    data['untaxed'] = _to_float(untaxed) if untaxed else (data['total'] - data.get('tax_amount', 0.0) if data['total'] else 0.0)
    # simple lines
    lines = []
    for m in _re.finditer(r'^(.*?)(?:\s{2,}|\t)+([0-9\.,]+)\s*(?:€|EUR)?\s*$', txt, _re.MULTILINE):
        desc = m.group(1).strip()
        amt = _to_float(m.group(2))
        if desc and amt and 2 < len(desc) < 120:
            lines.append({'name': desc, 'quantity': 1.0, 'price_unit': amt})
    data['lines'] = lines[:20]
    return data

class CfonOcrService(models.AbstractModel):
    _name = 'cfon.ocr.service'
    _description = 'OCR preprocessor + parser (bridge OCA)'

    def extract_text(self, file_bytes, filename):
        name = (filename or '').lower()
        txt = ''
        try:
            if name.endswith('.pdf'):
                try:
                    import pdfplumber, io as _io
                    with pdfplumber.open(_io.BytesIO(file_bytes)) as pdf:
                        for page in pdf.pages:
                            page_txt = page.extract_text() or ''
                            txt += page_txt + "\\n"
                except Exception:
                    from pypdf import PdfReader
                    import io as _io
                    reader = PdfReader(_io.BytesIO(file_bytes))
                    txt = "\\n".join([(p.extract_text() or '') for p in reader.pages])
            else:
                from PIL import Image
                import io as _io
                img = Image.open(_io.BytesIO(file_bytes))
                try:
                    import pytesseract
                    txt = pytesseract.image_to_string(img, lang='spa+eng')
                except Exception:
                    txt = ''
        except Exception as e:
            _logger.exception("Error leyendo archivo: %s", e)
        return txt or ''

    def ocr_if_needed(self, file_bytes, filename):
        # If PDF has no text, OCR page images
        name = (filename or '').lower()
        try:
            if name.endswith('.pdf'):
                import pdfplumber, io as _io
                with pdfplumber.open(_io.BytesIO(file_bytes)) as pdf:
                    text = "".join([(p.extract_text() or '') for p in pdf.pages])
                    if text.strip():
                        return text
                    # OCR each page as image
                    try:
                        import pytesseract
                        txt = ''
                        for p in pdf.pages:
                            img = p.to_image(resolution=300).original
                            txt += pytesseract.image_to_string(img, lang='spa+eng') + "\\n"
                        return txt
                    except Exception:
                        return ''
            else:
                return self.extract_text(file_bytes, filename)
        except Exception:
            return self.extract_text(file_bytes, filename)

    def import_with_oca_or_fallback(self, file_bytes, filename, create_partner=True):
        # Try delegate to OCA importer if present
        env = self.env
        txt = self.ocr_if_needed(file_bytes, filename)
        if env.registry.get('account.move') is None:
            raise UserError(_('Modelo account.move no disponible.'))
        partner = None
        parsed = parse_text_simple(txt)
        parsed['ocr_text'] = txt

        # Try OCA: create an attachment and call typical import entrypoint if available
        action = None
        try:
            # OCA often exposes a wizard; we simulate the minimal pathway by creating vendor bill ourselves,
            # because OCA entrypoints vary by version. We keep the behavior predictable.
            pass
        except Exception as e:
            _logger.info("No OCA importer path used: %s", e)

        # Fallback: create vendor bill draft
        Account = env['account.account'].sudo()
        Journal = env['account.journal'].sudo()
        Partner = env['res.partner'].sudo()
        # find partner
        if parsed.get('vat'):
            partner = Partner.search([('vat','=',parsed['vat'].strip())], limit=1)
        if not partner and parsed.get('partner_name'):
            partner = Partner.search([('name','ilike',parsed['partner_name'])], limit=1)
        if not partner and create_partner:
            partner = Partner.create({'name': parsed.get('partner_name') or 'Proveedor sin nombre', 'vat': (parsed.get('vat') or '').strip()})
        if not partner:
            raise UserError(_('No se pudo determinar/crear el proveedor para %s') % filename)

        account = Account.search([('internal_type','=','other'), ('deprecated','=',False)], limit=1)
        journal = Journal.search([('type','=','purchase')], limit=1)

        move_vals = {
            'move_type': 'in_invoice',
            'partner_id': partner.id,
            'invoice_date': parsed.get('date') or fields.Date.context_today(self),
            'invoice_origin': filename,
            'journal_id': journal.id,
            'currency_id': env.company.currency_id.id,
            'invoice_line_ids': [],
            'ref': parsed.get('number'),
        }
        lines = parsed.get('lines') or []
        if not lines:
            move_vals['invoice_line_ids'].append((0,0,{
                'name': parsed.get('number') or 'Factura importada',
                'quantity': 1.0,
                'price_unit': parsed.get('untaxed') or 0.0,
                'account_id': account.id,
            }))
        else:
            for l in lines:
                move_vals['invoice_line_ids'].append((0,0,{
                    'name': l.get('name') or 'Línea',
                    'quantity': l.get('quantity') or 1.0,
                    'price_unit': l.get('price_unit') or 0.0,
                    'account_id': account.id,
                }))
        move = env['account.move'].sudo().create(move_vals)
        # store OCR text
        try:
            move.ocr_source_text = parsed.get('ocr_text') or ''
        except Exception:
            pass
        move._recompute_dynamic_lines(recompute_all_taxes=True)
        return move
