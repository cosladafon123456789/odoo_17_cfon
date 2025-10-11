from odoo import models, fields

class RepairReasonWizard(models.TransientModel):
    _name = "repair.reason.wizard"
    _description = "Motivo de reparación (ejemplo)"

    reason = fields.Char("Motivo")
