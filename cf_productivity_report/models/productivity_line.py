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

    time_since_last = fields.Char(string='Tiempo desde anterior', compute='_compute_time_since_last')

    @api.depends('date', 'user_id', 'type')
    def _compute_time_since_last(self):
        for rec in self:
            if rec.type != 'order' or not rec.user_id or not rec.date:
                rec.time_since_last = '—'
                continue

            prev = self.search([
                ('user_id', '=', rec.user_id.id),
                ('type', '=', 'order'),
                ('date', '<', rec.date)
            ], order='date desc', limit=1)

            if prev:
                delta = rec.date - prev.date
                total_seconds = int(delta.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                rec.time_since_last = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                rec.time_since_last = '—'

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
        if not type_key or (user and user.name == "OdooBot"):
            return False
        return self.create({
            "user_id": user.id,
            "type": type_key,
            "reason": reason or False,
            "ref_model": ref_model or False,
            "ref_id": ref_id or False,
        })
