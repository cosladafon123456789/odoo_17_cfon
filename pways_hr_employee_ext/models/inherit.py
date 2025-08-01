from odoo import fields, models, api, _
from datetime import date
from odoo.exceptions import ValidationError

class HRVisaDesignation(models.Model):
    _name = 'hr.visa.designation'
    _description = 'Visa Designation'

    name = fields.Char(string='Name', required=True)


class HrJobCategory(models.Model):
    _name = 'hr.job.category'
    _description = 'Job Category'

    name = fields.Char(string='Name', required=True)

class HrHFMDepartment(models.Model):
    _name = 'hr.hfm.department'
    _description = 'Hr HFM Department'

    name = fields.Char(string='Name', required=True)


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    visa_designation = fields.Many2one('hr.visa.designation', string='Visa Designation')
    # division = fields.Selection([
    #     ('ids', 'IDS'),
    #     ('pds', 'PDS'),
    #     ('megadoor', 'Megadoor'),
    # ], string='Division', help='Select the company division')
    category_id = fields.Many2one('hr.job.category', string='Category 2')
    hr_hfm_department_id = fields.Many2one('hr.hfm.department', string='HFM Department')
    date_joining = fields.Date(string='Date Joining')
    service_age = fields.Char(string='Service Age', compute='_compute_service_age', store=True)
    birthday = fields.Date(string='Date of Birth', groups="hr.group_hr_user", tracking=True)
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    company_mol_code = fields.Char(
        string='Company MOL Code',
        help='The company’s Ministry of Labour registration code')
    date_of_leaving = fields.Date(string='Date of Leaving')
    air_ticket_start_date = fields.Date(string='Start Date')
    air_ticket_end_date = fields.Date(
        string='End Date',
        index=True,
        tracking=True,
        help="The end of the air ticket eligibility period."
    )

    @api.depends('birthday')
    def _compute_age(self):
        for record in self:
            if record.birthday:
                today = date.today()
                record.age = today.year - record.birthday.year - (
                    (today.month, today.day) < (record.birthday.month, record.birthday.day)
                )
            else:
                record.age = 0

    @api.depends('date_joining')
    def _compute_service_age(self):
      for record in self:
        if record.date_joining:
          today = date.today()
          delta = today - record.date_joining
          years = delta.days // 365
          months = (delta.days % 365) // 30
          record.service_age = f"{years} Year(s), {months} Month(s)"
        else:
          record.service_age = 'N/A'
