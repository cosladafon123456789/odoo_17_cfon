# -*- coding: utf-8 -*-
from odoo import api, models

class CFProductivityUpdateWizard(models.TransientModel):
    _name = "cf.productivity.update.wizard"
    _description = "Actualizar Resumen de Productividad"

    def action_update_now(self):
        return self.env["cf.productivity.summary"].action_update_productivity_summary()
