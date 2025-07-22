from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class VendorEvaluation(models.Model):
    _name = 'vendor.evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', copy=False, readonly=True, default='New')
    vendor_id    = fields.Many2one('res.partner',string='Vendor Name', required=True,)
    email = fields.Char(string='Email')
    phone_no = fields.Char(string="Phone")
    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date(string='End Date')
    manager_id = fields.Many2one('res.users',string='Manager', default=lambda self: self.env.user)
    date_entry = fields.Date(string='Entry Date',default=fields.Date.context_today)
    business_title = fields.Char(string='Business Title')
    evaluation_question_id = fields.Many2one('vendor.evaluation.question', string='Evaluation Question', required=True)
    line_ids = fields.One2many('vendor.evaluation.line', 'evaluation_id', string='Evaluation Lines')
    final_rating = fields.Selection([
        ('1', '★☆☆☆☆'),
        ('2', '★★☆☆☆'),
        ('3', '★★★☆☆'),
        ('4', '★★★★☆'),
        ('5', '★★★★★'),
    ], string='Final Evaluated')
    final_comment = fields.Text(string='Final Comment')
    final_point = fields.Float(string='Final Point')
    state = fields.Selection([
    ('draft', 'Draft'),
    ('request', 'Request Approval'),
    ('approve', 'Approved'),
    ('reject', 'Rejected'),
    ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, copy=False,)

    
    def action_calculate_final_rating(self):
        for rec in self:
            # Check for lines where applicable is True but rating is not given
            incomplete_lines = rec.line_ids.filtered(lambda l: l.is_applicable and not l.rating)
            if incomplete_lines:
                raise ValidationError(_("All applicable questions must have a rating before calculating final rating."))

            applicable_lines = rec.line_ids.filtered(lambda l: l.is_applicable and l.rating)
            ratings = [int(l.rating) for l in applicable_lines]

            if ratings:
                avg = sum(ratings) / len(ratings)
                rec.final_point = avg
                rec.final_rating = str(round(avg))

                # Update vendor's latest rating
                if rec.vendor_id:
                    rec.vendor_id.vendor_final_rating = rec.final_rating
            else:
                rec.final_point = 0.0
                rec.final_rating = False

                if rec.vendor_id:
                    rec.vendor_id.vendor_final_rating = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('vendor.evaluation') or 'New'
        records = super(VendorEvaluation, self).create(vals_list)
        return records

    @api.onchange('evaluation_question_id')
    def _onchange_evaluation_question_id(self):
        self.line_ids = [(5, 0, 0)]  # clear existing lines
        if self.evaluation_question_id:
            lines = []
            for question_line in self.evaluation_question_id.line_ids:
                lines.append((0, 0, {
                    'question_name': question_line.name,
                }))
            self.line_ids = lines
    

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_request_approval(self):
        for rec in self:
            rec.state = 'request'

    def action_approve(self):
        for rec in self:
            rec.state = 'approve'

    def action_reject(self):
        for rec in self:
            rec.state = 'reject'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'




class VendorEvaluationLine(models.Model):
    _name = 'vendor.evaluation.line'
    _description = 'Vendor Evaluation Line'
    _order = 'sequence'

    sequence = fields.Integer(string='No.', compute='_compute_sequence', store=True)
    question_name = fields.Char(string='Question', required=True)
    evaluation_id = fields.Many2one('vendor.evaluation', string='Evaluation')
    is_applicable = fields.Boolean(string='Applicable')
    rating = fields.Selection([
        ('1', '★☆☆☆☆'),
        ('2', '★★☆☆☆'),
        ('3', '★★★☆☆'),
        ('4', '★★★★☆'),
        ('5', '★★★★★'),
    ], string='Rating')
    note = fields.Char(string='Note')
    comment = fields.Char(string='Comment')


    @api.depends('evaluation_id.line_ids')
    def _compute_sequence(self):
        for rec in self:
            if rec.evaluation_id:
                for idx, line in enumerate(rec.evaluation_id.line_ids, start=1):
                    if line == rec:
                        rec.sequence = idx
                        break
            else:
                rec.sequence = 0