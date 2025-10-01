
from odoo import models, api, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def attendance_manual(self, next_action, entered_pin=None):
        """
        Parche v4:
        - Si la acción es salida, buscamos siempre un registro abierto y lo cerramos.
        - Si no hay registro abierto, creamos uno exprés con check_in y check_out = now.
        - Así nunca se queda colgado aunque el módulo de tracking falle.
        """
        now = fields.Datetime.now()
        Attendance = self.env['hr.attendance'].sudo()
        employee = self.env.user.employee_id

        if not employee:
            return {'action': next_action}

        # Si es salida, forzamos cierre de registro abierto
        if next_action in ('sign_out', 'check_out', 'action_sign_out'):
            open_att = Attendance.search([('employee_id', '=', employee.id), ('check_out', '=', False)], order='check_in desc', limit=1)
            if open_att:
                open_att.write({'check_out': now})
            else:
                # No había abierto -> creamos uno exprés
                Attendance.create({'employee_id': employee.id, 'check_in': now, 'check_out': now})
            return {'action': 'sign_out'}

        # Para entrada usamos el flujo estándar de Odoo
        res = super(HrEmployee, self).attendance_manual(next_action, entered_pin)
        return res
