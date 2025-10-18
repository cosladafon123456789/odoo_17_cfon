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
        ("ticket", "Ticket respondido"),
        ("order",  "Pedido/Entrega validada"),
    ], string="Tipo", required=True, index=True)
    reason = fields.Char("Motivo")
    ref_model = fields.Char("Modelo de referencia")
    ref_id = fields.Integer("ID referencia")
    average_time_20 = fields.Char("Tiempo medio (20 val.)", compute="_compute_avg_time_20", store=False)

    def _compute_avg_time_20(self):
        for rec in self:
            if rec.type != 'order':
                rec.average_time_20 = ''
                continue
            records = self.env['cf.productivity.line'].search([
                ('user_id', '=', rec.user_id.id),
                ('type', '=', 'order')
            ], order='date asc', limit=20)
            if len(records) < 2:
                rec.average_time_20 = '00:00:00'
                continue
            deltas = [(records[i].date - records[i-1].date).total_seconds() for i in range(1, len(records))]
            avg = sum(deltas) / len(deltas)
            hrs, rem = divmod(int(avg), 3600)
            mins, secs = divmod(rem, 60)
            rec.average_time_20 = f"{hrs:02}:{mins:02}:{secs:02}"

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