from odoo import models, fields

class RepairOrder(models.Model):
    _inherit = 'repair.order'

    state = fields.Selection(selection_add=[
        ('pending_part', 'Pendiente de pieza'),
    ], ondelete={'pending_part': 'set default'})

    def action_pending_part(self):
        for rec in self:
            rec.state = 'pending_part'
