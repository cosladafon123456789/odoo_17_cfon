from odoo import models, fields, api, _

class VendorEvaluationQuestion(models.Model):
    _name = 'vendor.evaluation.question'
    _description = 'Vendor Evaluation Question'

    
    name = fields.Char(string='Name')
    date = fields.Date(string='Date')
    line_ids = fields.One2many('vendor.evaluation.question.line', 'question_id', string='Questions')



class VendorEvaluationQuestionLine(models.Model):
    _name = 'vendor.evaluation.question.line'
    _description = 'Vendor Evaluation Question Line'

    name = fields.Char(string='Questions')
    question_id = fields.Many2one('vendor.evaluation.question', string='Question')