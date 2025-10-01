# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _ , fields
from odoo.http import request
from odoo.tools import float_round
from odoo.tools.image import image_data_uri
import pytz
import math
import time
from pytz import timezone
from datetime import datetime

class HrAttendanceTracking(http.Controller):

    @http.route('/bi_employee_company_transfer/emp_attendance_data', type="json", auth="user")
    def _get_employee_attendance_data(self):
        response = {}

        employee = request.env.user.employee_id if request.env.user.employee_id else request.env.user
        employee_ids = request.env['hr.employee'].search([
                    ('id','=',employee.id),
        ])
        hr_attendance_id = request.env['hr.attendance']

        for emp in employee_ids:
            if emp:
                employee_id = request.env['hr.employee'].search([
                    ('id','=',employee_ids.id),
                    ('resource_calendar_id','=','Standard 40 hours/week')
                ])
                
                
                if employee_id:
       
                        user_tz = pytz.timezone(request.env.context.get('tz') or request.env.user.tz or 'UTC')
                        check_in_time = pytz.UTC.localize(fields.Datetime.from_string(fields.Datetime.now()))
                        check_in = check_in_time.astimezone(user_tz).strftime('%Y-%m-%d %H:%M:%S')
                        check_in_hour = check_in_time.astimezone(user_tz).strftime('%Y-%m-%d %H:%M:%S')
                        attendance_check_in = datetime.strptime(check_in, '%Y-%m-%d %H:%M:%S')
                        day_week = attendance_check_in.weekday()
                        calendar_id = employee_id.resource_calendar_id
                        check_out_time = pytz.UTC.localize(fields.Datetime.from_string(fields.Datetime.now()))
                        check_out = check_out_time.astimezone(user_tz).strftime('%Y-%m-%d %H:%M:%S')
                        check_out_hour = check_out_time.astimezone(user_tz).strftime('%Y-%m-%d %H:%M:%S')
                        attendance_check_out = datetime.strptime(check_out, '%Y-%m-%d %H:%M:%S')
                        day_week = attendance_check_out.weekday()


                        if employee_id.attendance_state != 'checked_in':
                            checkin_resource_calendar_ids = request.env['resource.calendar.attendance'].search([('dayofweek','=',str(day_week)),
                                ('day_period','=','morning'),
                                ('calendar_id','=', calendar_id.id)
                                ], limit=1)
                            if checkin_resource_calendar_ids:
                                for val in checkin_resource_calendar_ids:
                                    hour_from = val.hour_from
                                    hour_from_str = str(val.hour_from)
                                    integer_part, fractional_part = hour_from_str.split('.')

                                    hour_from = int(integer_part)
                                    hour_from_min = fractional_part

                                    shiftHour = math.floor(val.hour_from)
                                    shiftMinute = (val.hour_from - shiftHour) * 60
                                    checkInTotalMinutes = attendance_check_in.hour * 60 + attendance_check_in.minute
                                    shiftTotalMinutes = shiftHour * 60 + shiftMinute
                                    differenceInMinutes = checkInTotalMinutes - shiftTotalMinutes

                                    differenceInHours = math.floor(differenceInMinutes / 60)
                                    
                                
                            response = {
                            'id': employee_id.id,
                            'attendance_state':employee_id.attendance_state,
                            'user_tz':user_tz,
                            'check_in':check_in,
                            'attendance_check_in':attendance_check_in.hour,
                            'check_in_hour':check_in_hour,
                            'attendance_check_in_min':attendance_check_in.minute,
                            'day_week':day_week,
                            'hour_from':hour_from,
                            'hour_from_min':hour_from_min,
                            'time_difference': str(differenceInHours) + ':' + str(attendance_check_in.minute),
                            'differenceInMinutes':differenceInMinutes,
                            
                            }

                        if employee_id.attendance_state == 'checked_in':
                            checkout_resource_calendar_ids = request.env['resource.calendar.attendance'].search([('dayofweek','=',str(day_week)),
                                ('day_period','=','afternoon'),
                                ('calendar_id','=', calendar_id.id)], limit=1)
                            if checkout_resource_calendar_ids:
                                for val in checkout_resource_calendar_ids:
                                    hour_from = val.hour_from
                                    hour_to_str = str(val.hour_to)
                                    integer_part, fractional_part = hour_to_str.split('.')

                                    hour_to = int(integer_part)
                                    hour_to_min = fractional_part

                                    shiftHour = math.floor(val.hour_to)
                                    shiftMinute = (val.hour_to - shiftHour) * 60

                                    checkOutTotalMinutes = attendance_check_out.hour * 60 + attendance_check_out.minute
                                    shiftTotalMinutes = shiftHour * 60 + shiftMinute
                                    differenceInMinutes = checkOutTotalMinutes - shiftTotalMinutes

                                    differenceInHours = math.floor(differenceInMinutes / 60)


                                response = {
                                    'id': employee_id.id,
                                    'attendance_state':employee_id.attendance_state,
                                    'user_tz':user_tz,
                                    'check_out_time':check_out_time,
                                    'check_out':check_out,
                                    'attendance_check_out':attendance_check_out.hour,
                                    'check_out_hours': attendance_check_out,
                                    'attendance_check_out_min':attendance_check_out.minute,
                                    'day_week':day_week,
                                    'time_difference': differenceInHours,
                                    'hour_from':hour_from if employee_id.attendance_state != "checked_in" else False,
                                    'hour_to':checkout_resource_calendar_ids.hour_to,
                                    'hour_to_min':hour_to_min,
                                    'differenceInMinutes':differenceInMinutes,
                                    'time_difference': str(differenceInHours) + ':' + str(attendance_check_out.minute)
                                }
                               
                
        
        # --- FIX SALIDA ---
        now_utc = fields.Datetime.now()
        try:
            diff = response.get('differenceInMinutes')
        except Exception:
            diff = None

        if diff is None:
            attendance = request.env['hr.attendance'].search([('employee_id', '=', employee_id.id), ('check_out', '=', False)], limit=1)
            if attendance:
                attendance.write({'check_out': now_utc})
            response['action'] = 'sign_out'
        else:
        now_utc = fields.Datetime.now()
        attendance = request.env['hr.attendance'].search([('employee_id', '=', employee_id.id), ('check_out', '=', False)], limit=1)
        if attendance:
            attendance.write({'check_out': now_utc})
        return {'action': 'sign_out'}
