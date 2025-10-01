# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
import pytz
import math


class CheckOutWizard(models.Model):
   
    _name = 'checkout.time.wizard'
    _description = "Check Out Wizard"

    check_out_delay_message = fields.Char(string="Check Out Delay Message",required=True)

    def action_ok(self):
        for rec in self:
            hr_attendance_id = self.env['hr.attendance'].sudo().browse(rec.ids)
            for val in hr_attendance_id:
                employee_id = self.env['hr.employee'].search([
                        ('name','=',rec.env.user.name),
                        ('resource_calendar_id','=','Standard 40 hours/week')
                    ])
                
                if employee_id.attendance_state == 'checked_in':
                    user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
                    check_out_time = pytz.UTC.localize(fields.Datetime.from_string(fields.Datetime.now()))
                    check_out = check_out_time.astimezone(user_tz).strftime('%Y-%m-%d %H:%M:%S')
                    check_out_hour = check_out_time.astimezone(user_tz).strftime('%Y-%m-%d %H:%M:%S')
                    attendance_check_out = datetime.strptime(check_out, '%Y-%m-%d %H:%M:%S')
                    day_week = attendance_check_out.weekday()
                    calendar_id = employee_id.resource_calendar_id
                    check_out_time = pytz.UTC.localize(fields.Datetime.from_string(fields.Datetime.now()))
                    check_out = check_out_time.astimezone(user_tz).strftime('%Y-%m-%d %H:%M:%S')
                    check_out_hour = check_out_time.astimezone(user_tz).strftime('%Y-%m-%d %H:%M:%S')
                    attendance_check_out = datetime.strptime(check_out, '%Y-%m-%d %H:%M:%S')
                    day_week = attendance_check_out.weekday()
                    resource_calendar_ids = self.env['resource.calendar.attendance'].search([('dayofweek','=',str(day_week)),
                                ('day_period','=','afternoon'),
                                ('calendar_id','=', calendar_id.id)], limit=1)
                    for val in resource_calendar_ids:

                        shiftHour = math.floor(val.hour_to)
                        shiftMinute = (val.hour_to - shiftHour) * 60
                        checkOutTotalMinutes = attendance_check_out.hour * 60 + attendance_check_out.minute
                        shiftTotalMinutes = shiftHour * 60 + shiftMinute
                        differenceOFInMinutes = checkOutTotalMinutes - shiftTotalMinutes
                        differenceInMinutes = int(differenceOFInMinutes)
                        differenceInHours = math.floor(differenceInMinutes / 60)
                        approval_id = self.env['hr.attendance.approval'].search([('employee_id','=',employee_id.id),('check_out','=',False)])
                        approval_id.write({
                            'check_out': fields.Datetime.now(),
                            'checkout_time_difference': False,
                            'check_out_delay_message':self.check_out_delay_message,
                        })
                        checkout_time_difference = str(differenceInHours) + ':' + str(differenceInMinutes)
                        approval_id.update({'checkout_time_difference':checkout_time_difference})
                
        
        return {'type': 'ir.actions.act_window_close'}