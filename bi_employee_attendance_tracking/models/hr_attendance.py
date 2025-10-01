# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime,timedelta,date
import pytz
import time
from odoo.exceptions import ValidationError


class HrAttendanceInherit(models.Model):
   
    _inherit = 'hr.attendance'

    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=True, tracking=True,compute="_compute_is_check_in",store=True,readonly=True)
    check_out = fields.Datetime(string="Check Out", tracking=True,compute="_compute_is_check_out",store=True,readonly=True)
    check_in_delay_message = fields.Char(string="Check In Delay Message",readonly=True)
    check_out_delay_message = fields.Char(string="Check Out Delay Message",readonly=True)
    is_check_in = fields.Boolean(string="is check in")
    is_check_out = fields.Boolean(string="is check out")
    checkin_time_difference = fields.Char(string="Checkin Time Difference")
    checkout_time_difference = fields.Char(string="Checkout Time Difference")
    checkin_time_wizard_id = fields.Many2one('checkin.time.wizard')
