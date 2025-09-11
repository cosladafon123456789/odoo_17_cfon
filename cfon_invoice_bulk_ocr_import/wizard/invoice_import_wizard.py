
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import base64

class InvoiceImportFile(models.TransientModel):
    _name = 'invoice.import.file'
    _description = 'Fichero para importación de factura'

    wizard_id = fields.Many2one('invoice.import.wizard', required=True, ondelete='cascade')
    name = fields.Char('Nombre de archivo', required=True)
    data = fields.Binary('Archivo', required=True, attachment=False)

class InvoiceImportWizard(models.TransientModel):
    _name = 'invoice.import.wizard'
    _description = 'Importación masiva de facturas (OCR)'
    
    file_ids = fields.One2many('invoice.import.file', 'wizard_id', string='Archivos')
    create_partner_if_missing = fields.Boolean('Crear proveedor si no existe', default=True)
    result_move_ids = fields.Many2many('account.move', string='Facturas creadas', readonly=True)

    def action_import(self):
        service = self.env['cfon.invoice.import.service']
        self.env['ir.config_parameter'].sudo().set_param('cfon_invoice_bulk.autocreate_partner', '1' if self.create_partner_if_missing else '0')
        moves = self.env['account.move']
        errors = []
        for rec in self.file_ids:
            file_bytes = base64.b64decode(rec.data)
            try:
                parsed = service.parse(file_bytes, rec.name)
                move = service.create_vendor_bill(parsed, rec.name)
                moves |= move
            except Exception as e:
                errors.append(f"{rec.name}: {str(e)}")
        self.result_move_ids = [(6,0,moves.ids)]
        if errors:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Resultado de importación'),
                'res_model': 'invoice.import.wizard',
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new',
                'context': {'errors': "\\n".join(errors)},
            }
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        action['domain'] = [('id','in', moves.ids)]
        return action
