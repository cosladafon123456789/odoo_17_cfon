
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import re, logging, io
from dateutil import parser as dtparser

_logger = logging.getLogger(__name__)

def _find_first(pattern, text, flags=re.IGNORECASE|re.MULTILINE):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else None

def _to_float(x):
    if not x:
        return 0.0
    s = x.replace(' ', '').replace('€','')
    if s.count(',')==1 and s.count('.')>=1 and s.rfind(',') > s.rfind('.'):
        s = s.replace('.', '').replace(',', '.')
    elif s.count(',')==1 and s.count('.')==0:
        s = s.replace(',', '.')
    try:
        return float(re.sub(r'[^0-9\.\-]', '', s))
    except Exception:
        return 0.0

def parse_invoice_text(txt):
    data = {}
    data['vat'] = _find_first(r'(?:NIF|CIF|VAT|N.?º\s*IVA)\s*[:\-]?\s*([A-Z0-9\-\.\s]+)', txt)
    data['partner_name'] = _find_first(r'^(?:Proveedor|Vendedor|Seller|Empresa)\s*[:\-]?\s*(.+)$', txt) or _find_first(r'^(.+?)\s*(?:S\.L\.|SL|S\.A\.|SA)\b', txt)
    data['number'] = _find_first(r'(?:Nº\s*Factura|Factura Nº|Invoice No\.?|Invoice #)\s*[:\-]?\s*([A-Z0-9\-/]+)', txt)
    date_raw = _find_first(r'(?:Fecha\s*[:\-]?|Date\s*[:\-]?)\s*([0-9]{1,2}[\-\/\.][0-9]{1,2}[\-\/\.][0-9]{2,4})', txt) or _find_first(r'(\d{4}[\-\/\.]\d{1,2}[\-\/\.]\d{1,2})', txt)
    if date_raw:
        try:
            data['date'] = dtparser.parse(date_raw, dayfirst=True).date().isoformat()
        except Exception:
            data['date'] = None
    else:
        data['date'] = None
    data['currency'] = _find_first(r'(?:Moneda|Currency)\s*[:\-]?\s*([A-Z]{3})', txt) or ('EUR' if '€' in txt else None)
    total = _find_first(r'(?:Total\s*Factura|Importe\s*Total|Total\s*Amount)\s*[:\-]?\s*([0-9\.,]+)', txt) or _find_first(r'\bTOTAL\b.*?([0-9\.,]+)', txt)
    tax = _find_first(r'(?:IVA|VAT)\s*(?:\(?(\d{1,2}(?:[\,\.]\d{1,2})?)%\)?)', txt)
    total_tax = _find_first(r'(?:IVA|VAT).*?([0-9\.,]+)\s*(?:€|EUR)?', txt)
    untaxed = _find_first(r'(?:Base\s*Imponible|Subtotal|Untaxed)\s*[:\-]?\s*([0-9\.,]+)', txt)
    data['total'] = _to_float(total)
    data['tax_percent'] = float(tax.replace(',', '.')) if tax else None
    data['tax_amount'] = _to_float(total_tax)
    data['untaxed'] = _to_float(untaxed) if untaxed else (data['total'] - data.get('tax_amount', 0.0) if data['total'] else 0.0)
    lines = []
    for m in re.finditer(r'^(.*?)(?:\s{2,}|\t)+([0-9\.,]+)\s*(?:€|EUR)?\s*$', txt, re.MULTILINE):
        desc = m.group(1).strip()
        amt = _to_float(m.group(2))
        if desc and amt and 2 < len(desc) < 120:
            lines.append({'name': desc, 'price_unit': amt, 'quantity': 1.0})
    data['lines'] = lines[:20]
    return data

class AccountMove(models.Model):
    _inherit = 'account.move'
    ocr_source_text = fields.Text(help="Texto crudo detectado por el OCR/lector.")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cfon_invoice_default_expense_account_id = fields.Many2one(
        'account.account',
        string='Cuenta de gasto por defecto',
        config_parameter='cfon_invoice_bulk.default_expense_account_id',
        domain="[('internal_type','=','other'), ('deprecated','=',False)]"
    )
    cfon_invoice_default_purchase_journal_id = fields.Many2one(
        'account.journal',
        string='Diario de facturas proveedor',
        config_parameter='cfon_invoice_bulk.default_purchase_journal_id',
        domain="[('type','=','purchase')]"
    )
    cfon_invoice_autocreate_partner = fields.Boolean(
        string='Crear proveedor automáticamente si no existe',
        config_parameter='cfon_invoice_bulk.autocreate_partner'
    )

def _get_param(env, key):
    return env['ir.config_parameter'].sudo().get_param(key)

class InvoiceImportService(models.AbstractModel):
    _name = 'cfon.invoice.import.service'
    _description = 'Servicio de importación/parseo de facturas (OCR)'

    def extract_text_from_file(self, file_bytes, filename):
        txt = ''
        name = (filename or '').lower()
        try:
            if name.endswith('.pdf'):
                try:
                    import pdfplumber
                    import io as _io
                    with pdfplumber.open(_io.BytesIO(file_bytes)) as pdf:
                        for page in pdf.pages:
                            page_text = page.extract_text() or ''
                            txt += page_text + "\n"
                except Exception:
                    from pypdf import PdfReader
                    import io as _io
                    reader = PdfReader(_io.BytesIO(file_bytes))
                    txt = "\n".join([(p.extract_text() or '') for p in reader.pages])
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
            _logger.exception("Error extrayendo texto: %s", e)
        return txt or ''

    def parse(self, file_bytes, filename):
        txt = self.extract_text_from_file(file_bytes, filename)
        data = parse_invoice_text(txt)
        data['ocr_text'] = txt
        return data

    def _find_or_create_partner(self, data):
        Partner = self.env['res.partner'].sudo()
        partner = None
        if data.get('vat'):
            partner = Partner.search([('vat','=',data['vat'].strip())], limit=1)
        if not partner and data.get('partner_name'):
            partner = Partner.search([('name','ilike',data['partner_name'])], limit=1)
        if not partner and _get_param(self.env, 'cfon_invoice_bulk.autocreate_partner') in ('1', True, 'True'):
            partner = Partner.create({'name': data.get('partner_name') or 'Proveedor sin nombre', 'vat': (data.get('vat') or '').strip()})
        return partner

    def _currency_id(self, currency_code):
        if not currency_code:
            return self.env.company.currency_id.id
        xmlid = f"base.{currency_code.lower()}"
        try:
            return self.env.ref(xmlid).id
        except Exception:
            return self.env.company.currency_id.id

    def create_vendor_bill(self, parsed, filename):
        Move = self.env['account.move'].sudo()
        Account = self.env['account.account'].sudo()
        Journal = self.env['account.journal'].sudo()

        journal_id = int(_get_param(self.env, 'cfon_invoice_bulk.default_purchase_journal_id') or 0) or Journal.search([('type','=','purchase')], limit=1).id
        account_id = int(_get_param(self.env, 'cfon_invoice_bulk.default_expense_account_id') or 0) or Account.search([('internal_type','=','other'), ('deprecated','=',False)], limit=1).id

        partner = self._find_or_create_partner(parsed)
        if not partner:
            raise UserError(_('No se pudo determinar/crear el proveedor para %s. Revise NIF/CIF o nombre en la factura.') % filename)

        move_vals = {
            'move_type': 'in_invoice',
            'partner_id': partner.id,
            'invoice_date': parsed.get('date') or fields.Date.context_today(self),
            'invoice_origin': filename,
            'invoice_payment_term_id': partner.property_supplier_payment_term_id.id,
            'journal_id': journal_id,
            'currency_id': self._currency_id(parsed.get('currency')),
            'invoice_line_ids': [],
            'ocr_source_text': parsed.get('ocr_text') or '',
            'ref': parsed.get('number'),
        }

        lines = parsed.get('lines') or []
        if not lines:
            price_subtotal = parsed.get('untaxed') or 0.0
            move_vals['invoice_line_ids'].append((0,0,{
                'name': parsed.get('number') or 'Factura importada',
                'quantity': 1.0,
                'price_unit': price_subtotal,
                'account_id': account_id,
            }))
        else:
            for l in lines:
                move_vals['invoice_line_ids'].append((0,0,{
                    'name': l.get('name') or 'Línea',
                    'quantity': l.get('quantity') or 1.0,
                    'price_unit': l.get('price_unit') or 0.0,
                    'account_id': account_id,
                }))

        move = Move.create(move_vals)
        if parsed.get('tax_percent') is not None:
            tax = self.env['account.tax'].search([('type_tax_use','=','purchase'), ('amount','=',parsed['tax_percent']), ('company_id','=',self.env.company.id)], limit=1)
            if tax:
                for line in move.invoice_line_ids:
                    line.tax_ids = [(6,0,[tax.id])]
        move._recompute_dynamic_lines(recompute_all_taxes=True)
        return move
