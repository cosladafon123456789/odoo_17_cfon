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
        ("order",  "Pedido/Entrega validada"),
    ], string="Tipo", required=True, index=True)
    reason = fields.Char("Motivo")
    ref_model = fields.Char("Modelo de referencia")
    ref_id = fields.Integer("ID referencia")
    duration_seconds = fields.Integer("Duración (segundos)", default=0, help="Tiempo dedicado estimado/real a la tarea")
    points = fields.Float("Puntos", compute="_compute_points", store=True)

    @api.depends("type")
    def _compute_points(self):
        for r in self:
            # Ponderación básica: reparación=2, pedido=1.5, ticket=1
            r.points = {"repair": 2.0, "order": 1.5, "ticket": 1.0}.get(r.type, 1.0)

    def name_get(self):
        res = []
        for r in self:
            name = f"{r.user_id.name or '-'} - {dict(self._fields['type'].selection).get(r.type)}"
            res.append((r.id, name))
        return res

    @api.model
    def log_entry(self, *, user=None, type_key=None, reason=None, ref_model=None, ref_id=None, duration_seconds=0):
        user = user or self.env.user
        if not type_key:
            return False
        return self.create({
            "user_id": user.id,
            "type": type_key,
            "reason": reason or False,
            "ref_model": ref_model or False,
            "ref_id": ref_id or False,
            "duration_seconds": duration_seconds or 0,
        })
