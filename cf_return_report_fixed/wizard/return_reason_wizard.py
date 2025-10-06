# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CfReturnReasonWizard(models.TransientModel):
    _name = "cf.return.reason.wizard"
    _description = "Wizard motivo de devolución (CF)"

    picking_id = fields.Many2one("stock.picking", required=True, readonly=True)
    reason_id = fields.Many2one("cf.return.reason", string="Motivo", required=True)
    note = fields.Char(string="Detalle")

    def action_confirm(self):
        self.ensure_one()
        picking = self.picking_id
        picking.write({
            "cf_return_reason_id": self.reason_id.id,
            "cf_return_reason_note": self.note or False,
        })
        # Llamar a la validación original indicando que ya está confirmado el motivo
        return picking.with_context(cf_return_reason_confirmed=True).button_validate()
