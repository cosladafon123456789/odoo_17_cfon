# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
import pytz
import math


class CheckInWizard(models.Model):
   
	_name = 'checkin.time.wizard'
	_description = "Check In Wizard"

	check_in_delay_message = fields.Char(string="Check In Delay Message",required=True)
	employee_id = fields.Many2one('hr.employee', string="Employee")

	def action_ok(self):
		for rec in self:
			hr_attendance_id = self.env['hr.attendance'].sudo().browse(rec.ids)
			for val in hr_attendance_id:
				employee_id = self.env['hr.employee'].search([
						('name','=',rec.env.user.name),
						('resource_calendar_id','=','Standard 40 hours/week')
					])
				user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
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
					resource_calendar_ids = self.env['resource.calendar.attendance'].search([('dayofweek','=',str(day_week)),
						('day_period','=','morning'),
						('calendar_id','=', calendar_id.id)
						], limit=1)
					for val in resource_calendar_ids:
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
								
						hr_attendance_approval_id  = self.env['hr.attendance.approval'].create({
							'employee_id':employee_id.id,
							'check_in': fields.Datetime.now(),
							'checkin_time_difference': False,
							'check_in_delay_message':self.check_in_delay_message,
						})
						checkin_time_difference = str(differenceInHours) + ':' + str(attendance_check_in.minute)
						hr_attendance_approval_id.update({'checkin_time_difference': checkin_time_difference})
						
						
		return {'type': 'ir.actions.act_window_close'}
		