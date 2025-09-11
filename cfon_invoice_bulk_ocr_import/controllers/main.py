
from odoo import http, _
from odoo.http import request
import base64

class CFONInvoiceImportController(http.Controller):

    @http.route('/cfon_invoice/import', type='http', auth='user', methods=['POST'], csrf=False)
    def import_files(self, **kwargs):
        files = request.httprequest.files.getlist('files[]') or request.httprequest.files.getlist('files')
        if not files:
            return request.make_response('No files', headers=[('Content-Type','text/plain')])
        Wizard = request.env['invoice.import.wizard'].sudo().create({
            'create_partner_if_missing': True,
        })
        for f in files:
            content = f.read()
            request.env['invoice.import.file'].sudo().create({
                'wizard_id': Wizard.id,
                'name': f.filename,
                'data': base64.b64encode(content),
            })
        # Execute import and return web client action
        action = Wizard.action_import()
        return request.make_json_response(action)
