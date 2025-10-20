from odoo import models, fields

class CFProductivityReport(models.Model):
    _name = 'cf.productivity.report'
    _description = 'Informe de productividad'

    fecha = fields.Datetime(string='Fecha', default=fields.Datetime.now)
    usuario_id = fields.Many2one('res.users', string='Usuario')
    tipo = fields.Char(string='Tipo')
    motivo = fields.Char(string='Motivo')
    modelo_referencia = fields.Char(string='Modelo de referencia')
    id_referencia = fields.Integer(string='ID referencia')
