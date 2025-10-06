# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
class StockPicking(models.Model):
    _inherit = "stock.picking"

    cf_return_reason_id = fields.Many2one("cf.return.reason", string="Motivo de devolución (CF)")
    cf_return_reason_note = fields.Char("Detalle motivo (CF)")
    cf_is_return = fields.Boolean("Es devolución (CF)", compute="_compute_cf_is_return", store=True)

    @api.depends("move_ids.move_orig_ids", "move_ids.origin_returned_move_id", "picking_type_code", "origin")
    def _compute_cf_is_return(self):
        for picking in self:
            is_return = False
            if any(m.origin_returned_move_id for m in picking.move_ids):
                is_return = True
            if not is_return and any(m.move_orig_ids for m in picking.move_ids):
                is_return = True
            if not is_return and picking.picking_type_code == "incoming" and picking.origin:
                is_return = True
            picking.cf_is_return = is_return

    def button_validate(self):
        self.ensure_one()
        # Siempre abrir wizard si es devolución
        if self.cf_is_return and not self.env.context.get("cf_return_reason_confirmed"):
            return {
                "name": _("Motivo de devolución"),
                "type": "ir.actions.act_window",
                "res_model": "cf.return.reason.wizard",
                "view_mode": "form",
                "target": "new",
                "context": {"default_picking_id": self.id},
            }
        # Tras pasar por wizard, validar normalmente
        return super(StockPicking, self).button_validate()
