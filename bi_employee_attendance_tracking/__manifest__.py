# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "Advanced Employee Attendance with Reason | Employee Attendance Late and Early Check out| HR Employee Attendance",
    "version": "17.0.0.0",
    "category": "Human Resources",
    "summary": "Advance attendance tracking Employee Check In/Out Time Employee early or late attendance summary Employee late attendance Payroll report Manage Late comers Employee early check out reason Hr Late Attendance details Employee late check out reason",
    "description": """ Late Check-in and Early Checkout Tracking with Reason module enhances attendance management by allowing real-time monitoring of employee check-ins and checkouts. It helps organisations track late arrivals and early departures while requiring employees to provide a reason. This promotes accountability and offers valuable insights into attendance patterns for better workforce management. """,
    "price": 25,
    "currency": "EUR",
    "author": "BROWSEINFO",
    'website': 'https://www.browseinfo.com/demo-request?app=bi_employee_attendance_tracking&version=17&edition=Community',
    'depends': ['base','hr','portal','utm','hr_attendance'],
    'data': [
        'security/hr_attendance_approval_rule.xml',
        'security/ir.model.access.csv',
        'security/res_groups.xml',       
        'views/hr_attendance_approval.xml',
        'views/hr_attendance_views.xml',
        'views/check_out_views.xml',
        'views/check_in_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'bi_employee_attendance_tracking/static/src/js/hr_attendance_inherit.js',
        ],

        'bi_employee_attendance_tracking.assets_public_attendance': [
             'bi_employee_attendance_tracking/static/src/js/hr_attendance_inherit.js',
              ]
    },
    'auto_install': False,
    'installable': True,
    "live_test_url":'https://www.browseinfo.com/demo-request?app=bi_employee_attendance_tracking&version=17&edition=Community',
    'license':'OPL-1',
    "images": ['static/description/Banner.gif'],

}

