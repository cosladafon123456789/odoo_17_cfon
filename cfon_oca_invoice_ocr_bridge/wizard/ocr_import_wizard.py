
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import base64

class CfonOcrImportFile(models.TransientModel):
    _name = 'cfon.ocr.import.file'
    _description = 'Fichero importación OCR (OCA bridge)'
    wizard_id = fields.Many2one('cfon.ocr.import.wizard', required=True, ondelete='cascade')
    name = fields.Char(required=True)
    data = fields.Binary(required=True, attachment=False)

class CfonOcrImportWizard(models.TransientModel):
    _name = 'cfon.ocr.import.wizard'
    _description = 'Importación masiva con OCR (puente OCA)'

    file_ids = fields.One2many('cfon.ocr.import.file', 'wizard_id', string='Archivos')
    create_partner_if_missing = fields.Boolean('Crear proveedor si no existe', default=True)
    result_move_ids = fields.Many2many('account.move', readonly=True)

    def action_import(self):
        service = self.env['cfon.ocr.service']
        moves = self.env['account.move']
        errors = []
        for rec in self.file_ids:
            fb = base64.b64decode(rec.data)
            try:
                move = service.import_with_oca_or_fallback(fb, rec.name, create_partner=self.create_partner_if_missing)
                moves |= move
            except Exception as e:
                errors.append(f"{rec.name}: {str(e)}")
        self.result_move_ids = [(6,0,moves.ids)]
        if errors:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Resultado de importación'),
                'res_model': 'cfon.ocr.import.wizard',
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new',
                'context': {'errors': "\\n".join(errors)},
            }
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        action['domain'] = [('id','in', moves.ids)]
        return action
