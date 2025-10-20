from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(StockPicking, self).button_validate()

        report_model = self.env['cf.productivity.report']
        for picking in self:
            report_model.create({
                'fecha': fields.Datetime.now(),
                'usuario_id': self.env.user.id,
                'tipo': 'Pedido/Entrega validada',
                'motivo': 'Entrega/Pedido validado',
                'modelo_referencia': 'stock.picking',
                'id_referencia': picking.id,
            })

        return res
