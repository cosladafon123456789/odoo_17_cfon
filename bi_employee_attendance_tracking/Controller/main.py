# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request


class AttendanceController(http.Controller):

    @http.route('/attendance/data', type='json', auth='user')
    def _get_employee_attendance_data(self, **kwargs):
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.uid)], limit=1)

        if not employee_id:
            return {'error': 'No employee linked to this user.'}

        # --- ENTRADA ---
        if employee_id.attendance_state != 'checked_in':
            # Si es entrada tardía, abre wizard de justificación (comportamiento original)
            response = {
                'action': {
                    'type': 'ir.actions.act_window',
                    'res_model': 'checkin.time.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_employee_id': employee_id.id,
                    }
                }
            }
            return response

        # --- SALIDA DIRECTA ---
        else:
            now_utc = fields.Datetime.now()
            attendance = request.env['hr.attendance'].sudo().search([
                ('employee_id', '=', employee_id.id),
                ('check_out', '=', False)
            ], limit=1)
            if attendance:
                attendance.write({'check_out': now_utc})
            return {'action': 'sign_out'}
