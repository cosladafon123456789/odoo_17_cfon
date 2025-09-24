# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime,timedelta,date
import pytz
import time
from pytz import timezone
from odoo.exceptions import ValidationError
from odoo.addons.resource.models.utils import Intervals


class HrAttendanceInherit(models.Model):
    _name = 'hr.attendance.approval'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Attendace Approval"
    _rec_name = 'employee_id'

    name = fields.Char()
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, ondelete='cascade', index=True)
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
        readonly=True)
    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=True, tracking=True,readonly=True)
    check_out = fields.Datetime(string="Check Out", tracking=True,readonly=True)
    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)
    color = fields.Integer(compute='_compute_color')
    overtime_hours = fields.Float(string="Over Time", compute='_compute_overtime_hours', store=True)
    in_latitude = fields.Float(string="Latitude", digits=(10, 7), readonly=True)
    in_longitude = fields.Float(string="Longitude", digits=(10, 7), readonly=True)
    in_country_name = fields.Char(string="Country", help="Based on IP Address", readonly=True)
    in_city = fields.Char(string="City", readonly=True)
    in_ip_address = fields.Char(string="IP Address", readonly=True)
    in_browser = fields.Char(string="Browser", readonly=True)
    in_mode = fields.Selection(string="Mode",
                               selection=[('kiosk', "Kiosk"),
                                          ('systray', "Systray"),
                                          ('manual', "Manual")],
                               readonly=True,
                               default='manual')
    out_latitude = fields.Float(digits=(10, 7), readonly=True)
    out_longitude = fields.Float(digits=(10, 7), readonly=True)
    out_country_name = fields.Char(help="Based on IP Address", readonly=True)
    out_city = fields.Char(readonly=True)
    out_ip_address = fields.Char(readonly=True)
    out_browser = fields.Char(readonly=True)
    out_mode = fields.Selection(selection=[('kiosk', "Kiosk"),
                                           ('systray', "Systray"),
                                           ('manual', "Manual")],
                                readonly=True,
                                default='manual')
    check_in_delay_message = fields.Char(string="Check In Delay Message",readonly=True)
    check_out_delay_message = fields.Char(string="Check Out Delay Message",readonly=True)
    checkin_time_difference = fields.Char(string="CheckIn Time Difference",readonly=True)
    checkout_time_difference = fields.Char(string="CheckOut Time Difference",readonly=True)
    state = fields.Selection([
        ('draft','Draft'),
        ('approve','Approved')],default='draft',compute="_compute_state",store=True)
    

    @api.depends('checkout_time_difference')
    def _compute_state(self):
        for rec in self:
            if rec.checkout_time_difference:
                rec.update({'state':'draft'})

    def action_approve(self):
        for rec in self:
            rec.update({'state':'approve'})
            if rec.employee_id.attendance_state != 'checked_in':
                user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
                check_in_time = pytz.UTC.localize(fields.Datetime.from_string(fields.Datetime.now()))
                check_in = check_in_time.astimezone(user_tz).strftime('%Y-%m-%d %H:%M:%S')
                check_in_hour = check_in_time.astimezone(user_tz).strftime('%Y-%m-%d %H:%M:%S')
                attendance_check_in = datetime.strptime(check_in, '%Y-%m-%d %H:%M:%S')
                day_week = attendance_check_in.weekday()
                calendar_id = rec.employee_id.resource_calendar_id
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

                    if attendance_check_in.hour > val.hour_from or (attendance_check_in.hour >= val.hour_from and attendance_check_in.minute > int(hour_from_min)) :
                        self.env['hr.attendance'].create({
                            'employee_id':rec.employee_id.id,
                            'check_in':rec.check_in,
                            'checkin_time_difference':rec.checkin_time_difference,
                            'check_in_delay_message':rec.check_in_delay_message,
                        })
                        rec.message_post(body=_("Late Check In Approved"))
                    
           
            else:
                user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
                check_out_time = pytz.UTC.localize(fields.Datetime.from_string(fields.Datetime.now()))
                check_out = check_out_time.astimezone(user_tz).strftime('%Y-%m-%d %H:%M:%S')
                check_out_hour = check_out_time.astimezone(user_tz).strftime('%Y-%m-%d %H:%M:%S')
                attendance_check_out = datetime.strptime(check_out, '%Y-%m-%d %H:%M:%S')
                day_week = attendance_check_out.weekday()
                calendar_id = rec.employee_id.resource_calendar_id
                
                resource_calendar_ids = self.env['resource.calendar.attendance'].search([('dayofweek','=',str(day_week)),
						('day_period','=','afternoon'),
						('calendar_id','=', calendar_id.id)
						], limit=1)

                for val in resource_calendar_ids:
                    hour_to_str = str(val.hour_to)
                    integer_part, fractional_part = hour_to_str.split('.')
                    hour_to = int(integer_part)
                    hour_to_min = fractional_part
                    attendance_id = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id),('check_out','=',False)])

                    if attendance_check_out.hour > val.hour_to or ( attendance_check_out.hour >= val.hour_to and  attendance_check_out.minute > int(hour_to_min)) :
                        attendance_id.write({
                            'check_out':rec.check_out,
                            'checkout_time_difference':rec.checkout_time_difference,
                            'check_out_delay_message':rec.check_out_delay_message,
                            
                        })
                        rec.update({'state':'approve'})
                        rec.message_post(body=_("Late Check Out Approved"))
                    else:
                        attendance_id.write({
                            'check_out':attendance_check_out
                          
                            })
            

