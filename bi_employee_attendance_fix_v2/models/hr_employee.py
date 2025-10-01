from odoo import models, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def attendance_manual(self, next_action, entered_pin=None):
        """
        Parche v2: llamamos directamente al método original de Odoo,
        ignorando el override roto del módulo bi_employee_attendance_tracking.
        """
        res = super(HrEmployee, self).attendance_manual(next_action, entered_pin)

        # Hook para lógica adicional de tracking (opcional)
        if res and isinstance(res, dict) and res.get('action'):
            employee = self.env.user.employee_id
            if employee:
                employee.message_post(
                    body=f"Fichaje realizado: {next_action}",
                    message_type="notification"
                )
        return res
