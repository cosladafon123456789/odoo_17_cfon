from odoo import api, fields, models, _
from odoo.exceptions import UserError

class RepairReasonWizard(models.TransientModel):
    _name = "repair.reason.wizard"
    _description = "Seleccionar motivo de reparación"

    repair_reason_id = fields.Many2one("cf.repair.reason", string="Motivo", required=True)

    def action_confirm(self):
        repair = self.env["repair.order"].browse(self.env.context.get("active_id"))
        if not repair:
            raise UserError(_("No se encontró la reparación activa."))
        repair.repair_reason_id = self.repair_reason_id.id
        # Llama al flujo que completa y registra
        return repair.action_repair_done_with_reason()
