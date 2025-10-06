# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CfReturnDashboard(models.TransientModel):
    _name = "cf.return.dashboard"
    _description = "Panel KPI de Devoluciones (CF)"
    _transient_max_hours = 0.1

    total_returns = fields.Integer(string="Devoluciones totales", compute="_compute_counts")
    pending_returns = fields.Integer(string="Pendientes", compute="_compute_counts")
    received_returns = fields.Integer(string="Recibidas", compute="_compute_counts")
    rejected_returns = fields.Integer(string="Rechazadas", compute="_compute_counts")

    @api.depends()
    def _compute_counts(self):
        Picking = self.env["stock.picking"]
        for rec in self:
            domain_return = [("cf_is_return", "=", True)]
            rec.total_returns = Picking.search_count(domain_return)
            rec.pending_returns = Picking.search_count(domain_return + [("state", "not in", ["done", "cancel"])])
            rec.received_returns = Picking.search_count(domain_return + [("state", "=", "done")])
            rec.rejected_returns = Picking.search_count(domain_return + [("state", "=", "cancel")])

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        # ensures one record is shown
        return vals
