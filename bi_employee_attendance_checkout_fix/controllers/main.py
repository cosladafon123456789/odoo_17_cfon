
from odoo import http, fields
from odoo.http import request
import pytz
from datetime import datetime
import math

class HrAttendanceCheckoutFix(http.Controller):
    @http.route('/bi_employee_company_transfer/emp_attendance_data', type="json", auth="user")
    def _get_employee_attendance_data(self):
        """
        Parche para gestionar salida correctamente:
        - Si la salida es en horario -> cierra check_out directamente.
        - Si es fuera de horario -> abre wizard checkout.time.wizard.
        - La entrada sigue el flujo original (wizard si aplica).
        """
        response = {}
        employee = request.env.user.employee_id
        if not employee:
            return {'action': 'none'}

        user_tz = pytz.timezone(request.env.context.get('tz') or request.env.user.tz or 'UTC')
        now_utc = fields.Datetime.now()
        now_local = pytz.UTC.localize(fields.Datetime.from_string(str(now_utc))).astimezone(user_tz)
        attendance_dt = datetime.strptime(now_local.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        day_week = attendance_dt.weekday()

        # Entrada (flujo original simplificado)
        if employee.attendance_state != 'checked_in':
            response['action'] = 'sign_in'
            return response

        # Salida
        calendar_id = employee.resource_calendar_id
        if not calendar_id:
            attendance = request.env['hr.attendance'].search([('employee_id', '=', employee.id), ('check_out', '=', False)], limit=1)
            if attendance:
                attendance.write({'check_out': now_utc})
            return {'action': 'sign_out'}

        checkout_resource_calendar_ids = request.env['resource.calendar.attendance'].search([
            ('dayofweek','=',str(day_week)),
            ('day_period','=','afternoon'),
            ('calendar_id','=', calendar_id.id)
        ], limit=1)

        if checkout_resource_calendar_ids:
            shiftHour = math.floor(checkout_resource_calendar_ids.hour_to)
            shiftMinute = (checkout_resource_calendar_ids.hour_to - shiftHour) * 60
            checkOutTotalMinutes = attendance_dt.hour * 60 + attendance_dt.minute
            shiftTotalMinutes = shiftHour * 60 + shiftMinute
            differenceInMinutes = checkOutTotalMinutes - shiftTotalMinutes

            if differenceInMinutes == 0:
                attendance = request.env['hr.attendance'].search([('employee_id', '=', employee.id), ('check_out', '=', False)], limit=1)
                if attendance:
                    attendance.write({'check_out': now_utc})
                return {'action': 'sign_out'}
            else:
                return {
                    'action': {
                        'type': 'ir.actions.act_window',
                        'res_model': 'checkout.time.wizard',
                        'view_mode': 'form',
                        'target': 'new',
                        'context': {
                            'default_employee_id': employee.id,
                            'default_difference': differenceInMinutes,
                        }
                    }
                }

        attendance = request.env['hr.attendance'].search([('employee_id', '=', employee.id), ('check_out', '=', False)], limit=1)
        if attendance:
            attendance.write({'check_out': now_utc})
        return {'action': 'sign_out'}
