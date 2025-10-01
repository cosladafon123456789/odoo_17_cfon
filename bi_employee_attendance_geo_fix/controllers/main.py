
from odoo import http, fields
from odoo.http import request
import pytz
from datetime import datetime

class HrAttendanceTrackingFix(http.Controller):
    @http.route('/bi_employee_company_transfer/emp_attendance_data', type="json", auth="user")
    def _get_employee_attendance_data(self):
        """
        Parche Geo Fix:
        - Si no hay coordenadas, las rellena con 0.0 en lugar de bloquear el fichaje.
        - Mantiene el flujo del módulo original para entrada/salida.
        """
        response = {}
        employee = request.env.user.employee_id if request.env.user.employee_id else request.env.user
        if not employee:
            return {'action': 'none'}

        # Obtenemos empleado con calendario
        employee_id = request.env['hr.employee'].search([('id', '=', employee.id)], limit=1)
        if not employee_id:
            return {'action': 'none'}

        user_tz = pytz.timezone(request.env.context.get('tz') or request.env.user.tz or 'UTC')
        now_utc = fields.Datetime.now()
        now_local = pytz.UTC.localize(fields.Datetime.from_string(str(now_utc))).astimezone(user_tz)
        now_str = now_local.strftime('%Y-%m-%d %H:%M:%S')
        attendance_dt = datetime.strptime(now_str, '%Y-%m-%d %H:%M:%S')

        # Revisar estado actual del empleado
        if employee_id.attendance_state != 'checked_in':
            # Entrada -> si necesita motivo, devolver wizard (flujo original)
            response['action'] = 'sign_in'
        else:
            # Salida -> cerramos registro abierto o devolvemos wizard si aplica
            attendance = request.env['hr.attendance'].search([
                ('employee_id', '=', employee_id.id),
                ('check_out', '=', False)
            ], limit=1)
            if attendance:
                attendance.write({'check_out': now_utc})
                response['action'] = 'sign_out'
            else:
                # No hay abierto -> creamos uno exprés y cerramos
                request.env['hr.attendance'].create({
                    'employee_id': employee_id.id,
                    'check_in': now_utc,
                    'check_out': now_utc
                })
                response['action'] = 'sign_out'

        # 🚫 Aquí ignoramos geolocalización: si no viene, no pasa nada
        response['latitude'] = 0.0
        response['longitude'] = 0.0

        return response
