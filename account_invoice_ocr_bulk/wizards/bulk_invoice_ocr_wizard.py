
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import base64
import logging

_logger = logging.getLogger(__name__)

class BulkInvoiceOCRWizard(models.TransientModel):
    _name = "bulk.invoice.ocr.wizard"
    _description = "Subir facturas (OCR masivo)"

    file_ids = fields.One2many("bulk.invoice.ocr.line", "wizard_id", string="Archivos")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    journal_id = fields.Many2one(
        "account.journal",
        string="Diario de compras",
        required=True,
        domain="[('type','=','purchase'), ('company_id','=',company_id)]",
        default=lambda self: self.env['account.journal'].search([('type','=','purchase'), ('company_id','=',self.env.company.id)], limit=1),
    )
    default_partner_id = fields.Many2one("res.partner", string="Proveedor por defecto")

    def action_process(self):
        self.ensure_one()
        if not self.file_ids:
            raise UserError(_("Añade al menos un archivo."))

        created_moves = self.env['account.move']
        errors = []

        for line in self.file_ids:
            try:
                move = self._create_bill_from_file(line)
                created_moves |= move
            except Exception as e:
                _logger.exception("OCR error")
                errors.append(f"{line.filename or 'archivo'}: {str(e)}")

        action = {
            "type": "ir.actions.act_window",
            "name": _("Facturas proveedor creadas"),
            "res_model": "account.move",
            "view_mode": "tree,form",
            "domain": [("id", "in", created_moves.ids)],
        }
        if errors:
            msg = _("Se crearon %s facturas. Algunos archivos fallaron:\n- %s") % (len(created_moves), "\n- ".join(errors))
            # show as warning in chatter later; for now use a pop-up
            return {
                "warning": {"title": _("OCR con incidencias"), "message": msg},
                **action,
            }
        return action

    def _create_bill_from_file(self, line):
        Move = self.env['account.move'].with_context(default_move_type='in_invoice')
        text = self._extract_text_from_file(line.datas, line.filename or '')
        parsed = self._parse_invoice_text(text) if text else {}

        # Partner resolution
        partner = False
        vat = (parsed.get('vat') or '').upper().replace('ES','').replace(' ', '')
        if vat:
            partner = self.env['res.partner'].search([('vat','ilike', vat)], limit=1)
        if not partner and parsed.get('supplier_name'):
            partner = self.env['res.partner'].search([('name','ilike', parsed['supplier_name'])], limit=1)
        if not partner:
            partner = self.default_partner_id
        if not partner:
            # create a generic vendor once
            partner = self.env['res.partner'].search([('name','=','Proveedor Genérico OCR'), ('supplier_rank','>',0)], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': 'Proveedor Genérico OCR',
                    'supplier_rank': 1,
                    'company_type': 'company',
                })

        # Total amount
        amount_total = parsed.get('total_amount') or 0.0
        if amount_total <= 0.0:
            amount_total = 0.0

        # Fallback product/account line
        account = self.journal_id.default_account_id or self.env['account.account'].search([
            ('company_id','=', self.company_id.id),
            ('internal_type','=','expense')
        ], limit=1)
        if not account:
            raise UserError(_("No se encontró una cuenta de gasto para la compañía."))

        line_vals = {
            'name': parsed.get('description') or 'Gasto OCR',
            'account_id': account.id,
            'quantity': 1.0,
            'price_unit': amount_total or 0.0,
        }

        move_vals = {
            'move_type': 'in_invoice',
            'partner_id': partner.id,
            'invoice_date': parsed.get('date'),
            'invoice_origin': parsed.get('invoice_number'),
            'journal_id': self.journal_id.id,
            'invoice_line_ids': [(0,0,line_vals)],
        }
        move = Move.create(move_vals)

        # Attach original file
        self.env['ir.attachment'].create({
            'name': line.filename or 'invoice.pdf',
            'res_model': 'account.move',
            'res_id': move.id,
            'datas': line.datas,
            'mimetype': line.mimetype or 'application/pdf',
        })

        # Log parsed info
        note = _("OCR detectado → Proveedor: %s | CIF/NIF: %s | Nº factura: %s | Fecha: %s | Total: %s") % (
            partner.display_name,
            parsed.get('vat') or '',
            parsed.get('invoice_number') or '',
            parsed.get('date') or '',
            parsed.get('total_amount') or '',
        )
        move.message_post(body=note)

        return move

    # --- utils ---
    def _extract_text_from_file(self, datas, filename):
        binary = base64.b64decode(datas or b"")
        name_lower = (filename or '').lower()
        # Prefer pdfminer for PDFs
        if name_lower.endswith('.pdf'):
            try:
                from pdfminer.high_level import extract_text
                import io
                with io.BytesIO(binary) as fh:
                    txt = extract_text(fh) or ""
                    return txt
            except Exception as e:
                _logger.warning("Fallo pdfminer: %s", e)
        # Fallback to plain bytes decode
        try:
            return binary.decode('utf-8', errors='ignore')
        except Exception:
            return ""

    def _parse_invoice_text(self, text):
        import re
        from datetime import datetime

        data = {}

        # VAT (ES formats rough)
        vat_match = re.search(r'\b(?:ES)?([A-Z]\d{7}[A-Z]|\d{8}[A-Z]|[A-Z]{2}\d{9})\b', text, re.IGNORECASE)
        if vat_match:
            data['vat'] = vat_match.group(0)

        # Invoice number keywords
        num_match = re.search(r'(?:Factura|N[ºo]\s*Factura|Invoice)\s*[:#]?\s*([A-Z0-9\-\/\.]+)', text, re.IGNORECASE)
        if num_match:
            data['invoice_number'] = num_match.group(1).strip()

        # Date detection (dd/mm/yyyy or yyyy-mm-dd)
        date_match = re.search(r'(\b\d{2}[\/\-]\d{2}[\/\-]\d{4}\b|\b\d{4}[\/\-]\d{2}[\/\-]\d{2}\b)', text)
        if date_match:
            raw = date_match.group(1)
            for fmt in ("%d/%m/%Y","%d-%m-%Y","%Y-%m-%d","%Y/%m/%d"):
                try:
                    data['date'] = datetime.strptime(raw, fmt).date()
                    break
                except Exception:
                    continue

        # Total amount near keywords
        tot_match = re.search(r'(Total|Importe\s*total|Total\s*a\s*pagar)\D{0,20}(\d{1,3}(?:[\.\s]\d{3})*(?:,\d{2})|\d+\.\d{2})', text, re.IGNORECASE)
        if tot_match:
            amt = tot_match.group(2)
            amt = amt.replace('.', '').replace(' ', '').replace(',', '.')
            try:
                data['total_amount'] = float(amt)
            except Exception:
                pass

        # Supplier name heuristic (first line with "S.L."/"S.A." or uppercase words)
        name_match = re.search(r'([A-ZÁÉÍÓÚÑ0-9][A-ZÁÉÍÓÚÑ&\.\-\s]{5,}(?:S\.L\.|S\.A\.|SL|SA))', text)
        if name_match:
            data['supplier_name'] = name_match.group(1).strip()

        # brief description
        data['description'] = "Factura OCR"
        return data


class BulkInvoiceOCRLine(models.TransientModel):
    _name = "bulk.invoice.ocr.line"
    _description = "Línea archivo OCR"

    wizard_id = fields.Many2one("bulk.invoice.ocr.wizard", required=True, ondelete="cascade")
    datas = fields.Binary("Archivo", required=True)
    filename = fields.Char("Nombre de archivo")
    mimetype = fields.Char("MIME")

