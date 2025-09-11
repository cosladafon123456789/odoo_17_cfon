# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date

class AccountVendorBillUploadWizard(models.TransientModel):
    _name = 'account.vendor.bill.upload.wizard'
    _description = 'Subir facturas proveedor (PDF) - Creador masivo de borradores'
    
    company_id = fields.Many2one('res.company', string='Compañía', required=True, default=lambda self: self.env.company)
    journal_id = fields.Many2one(
        'account.journal', 
        string='Diario de compras',
        domain="[('type', '=', 'purchase'), ('company_id', '=', company_id)]",
        help='Diario donde se crearán las facturas proveedor.',
    )
    invoice_date = fields.Date(string='Fecha factura', default=lambda self: date.today())
    upload_files = fields.Many2many(
        'ir.attachment', 
        string='Archivos PDF', 
        help='Arrastra y suelta aquí uno o varios archivos PDF.',
    )
    default_partner_id = fields.Many2one('res.partner', string='Proveedor por defecto')
    set_filename_in_ref = fields.Boolean(string='Usar nombre del archivo como Referencia proveedor', default=True)
    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        company = self.env.company
        journal = self.env['account.journal'].search([('type','=','purchase'), ('company_id','=',company.id)], limit=1)
        if journal:
            res['journal_id'] = journal.id
        return res
    
    def action_create_bills(self):
        self.ensure_one()
        if not self.upload_files:
            raise UserError(_('Debes añadir al menos un archivo PDF.'))
        if not self.journal_id:
            raise UserError(_('No se encontró un Diario de compras para la compañía. Configura uno.'))
        
        created_moves = self.env['account.move']
        for att in self.upload_files:
            if (att.mimetype or '').lower() not in ('application/pdf', 'pdf'):
                # Permitimos también adjuntos sin mimetype, pero advertimos más adelante
                pass
            
            vals = {
                'move_type': 'in_invoice',
                'company_id': self.company_id.id,
                'journal_id': self.journal_id.id,
                'invoice_date': self.invoice_date,
            }
            if self.default_partner_id:
                vals['partner_id'] = self.default_partner_id.id
            if self.set_filename_in_ref and att.name:
                vals['ref'] = att.name
            
            # Crear factura en borrador
            move = self.env['account.move'].create(vals)
            
            # Añadir una línea placeholder (0€) para permitir guardar
            self.env['account.move.line'].create({
                'move_id': move.id,
                'name': _('Pendiente de datos'),
                'quantity': 1.0,
                'price_unit': 0.0,
                'account_id': self.journal_id.default_account_id.id or self.env['account.account'].search([('company_id','=',self.company_id.id)], limit=1).id,
            })
            
            # Re-asociar/duplicar el attachment a la factura
            att_copy = att.with_context(no_document=True).copy(default={
                'res_model': 'account.move',
                'res_id': move.id,
            })
            # marcar como documento principal (etiqueta) si está disponible
            if 'attachment_ids' in move._fields:
                pass  # handled by chatter
            
            created_moves |= move
        
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        action['domain'] = [('id', 'in', created_moves.ids)]
        action['context'] = {'create': False}
        action['name'] = _('Facturas creadas: %s') % len(created_moves)
        return action
