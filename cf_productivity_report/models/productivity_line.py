# -*- coding: utf-8 -*-
from odoo import api, fields, models

class CFProductivityLine(models.Model):
    _name = "cf.productivity.line"
    _description = "CF Productividad - Registro"
    _order = "date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    date = fields.Datetime("Fecha", default=lambda self: fields.Datetime.now(), index=True)
    user_id = fields.Many2one("res.users", "Usuario", required=True, index=True)
    type = fields.Selection([
        ("repair", "Reparación"),
        ("ticket", "Ticket respondido"),
        ("ticket_stage", "Cambio de etapa de ticket"),
        ("order",  "Pedido/Entrega validada"),
    ], string="Tipo", required=True, index=True)

    reason = fields.Char("Motivo/Detalle")
    ref_model = fields.Char("Modelo relacionado")
    ref_id = fields.Integer("ID relacionado")

    # Intervalo entre esta acción y la anterior del mismo tipo/usuario
    interval_seconds = fields.Integer(
        "Intervalo (seg.)",
        help="Segundos transcurridos desde la última acción comparable del mismo usuario.",
        group_operator="avg",
        index=True,
        copy=False,
    )
    interval_hhmmss = fields.Char(
        "Intervalo (hh:mm:ss)",
        compute="_compute_interval_hhmmss",
        store=False
    )

    @api.depends("interval_seconds")
    def _compute_interval_hhmmss(self):
        for rec in self:
            s = rec.interval_seconds or 0
            h = s // 3600
            m = (s % 3600) // 60
            sec = s % 60
            rec.interval_hhmmss = f"{h:02d}:{m:02d}:{sec:02d}"

    @api.model
    def log_entry(self, *, user=None, type_key=None, reason=None, ref_model=None, ref_id=None, interval_seconds=None):
        user = user or self.env.user
        if not type_key:
            return False
        return self.create({
            "user_id": user.id,
            "type": type_key,
            "reason": reason or False,
            "ref_model": ref_model or False,
            "ref_id": ref_id or False,
            "interval_seconds": interval_seconds if interval_seconds is not None else False,
        })
