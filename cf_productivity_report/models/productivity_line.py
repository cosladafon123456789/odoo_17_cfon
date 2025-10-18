# -*- coding: utf-8 -*-
from odoo import api, fields, models

class CFProductivityLine(models.Model):
    _name = "cf.productivity.line"
    _description = "Registro de productividad"
    _order = "date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    date = fields.Datetime("Fecha", default=lambda self: fields.Datetime.now(), index=True)
    user_id = fields.Many2one("res.users", "Usuario", required=True, index=True)
    type = fields.Selection([
        ("repair", "Reparación"),
        ("ticket", "Ticket respondido / gestionado"),
        ("order",  "Pedido/Entrega validada"),
    ], string="Tipo", required=True, index=True)
    reason = fields.Char("Motivo")
    ref_model = fields.Char("Modelo de referencia")
    ref_id = fields.Integer("ID referencia")

    def name_get(self):
        res = []
        for r in self:
            sel = dict(self._fields['type'].selection)
            name = f"{r.user_id.name or '-'} - {sel.get(r.type)}"
            res.append((r.id, name))
        return res

    @api.model
    def log_entry(self, *, user=None, type_key=None, reason=None, ref_model=None, ref_id=None):
        user = user or self.env.user
        if not type_key:
            return False
        return self.create({
            "user_id": user.id,
            "type": type_key,
            "reason": reason or False,
            "ref_model": ref_model or False,
            "ref_id": ref_id or False,
        })