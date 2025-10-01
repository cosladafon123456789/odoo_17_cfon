from odoo import models, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def attendance_manual(self, next_action, entered_pin=None):
        """
        Parche: aseguramos que el fichaje normal funcione devolviendo super(),
        pero mantenemos el tracking extra del módulo original.
        """
        res = super().attendance_manual(next_action, entered_pin)

        # Hook para lógica adicional de tracking
        if res and res.get('action'):
            employee = self.env.user.employee_id
            if employee:
                employee.message_post(
                    body=f"Fichaje realizado: {next_action}",
                    message_type="notification"
                )

        return res
