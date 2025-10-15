from odoo import models, fields

class RepairOrder(models.Model):
    _inherit = 'repair.order'

    state = fields.Selection(selection_add=[
        ('pending_part', 'Pendiente de pieza'),
    ], ondelete={'pending_part': 'set default'})

    def action_pending_part(self):
        """Cambia el estado a Pendiente de pieza"""
        for record in self:
            record.state = 'pending_part'
