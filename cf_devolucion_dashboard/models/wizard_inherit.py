from odoo import fields, models

class DevolucionWizardInherit(models.TransientModel):
    _inherit = "cf.devolucion.wizard"

    def action_confirm(self):
        self.ensure_one()
        order = self.sale_order_id
        if order and not order.fecha_devolucion:
            order.fecha_devolucion = fields.Datetime.now()
        return super().action_confirm()