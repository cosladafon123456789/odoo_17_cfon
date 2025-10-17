# -*- coding: utf-8 -*-
from odoo import api, fields, models

class CFProductivityLine(models.Model):
    _name = "cf.productivity.line"
    _description = "CF Productividad - Registro"
    _order = "date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    date = fields.Datetime(
        "Fecha",
        default=lambda self: fields.Datetime.now(),
        index=True,
        tracking=True,
    )
    user_id = fields.Many2one(
        "res.users",
        "Usuario",
        required=True,
        index=True,
        tracking=True,
    )
    type = fields.Selection(
        [
            ("repair", "Reparación"),
            ("ticket", "Ticket respondido"),
            ("order",  "Pedido/Entrega validada"),
        ],
        string="Tipo",
        required=True,
        index=True,
        tracking=True,
    )
    reason = fields.Char("Motivo / Detalle", tracking=True)
    ref = fields.Reference(
        selection=[
            ("repair.order", "Reparación"),
            ("helpdesk.ticket", "Ticket"),
            ("stock.picking", "Albarán"),
        ],
        string="Relacionado",
        index=True,
    )

    def name_get(self):
        res = []
        for r in self:
            tdict = dict(self._fields['type'].selection)
            d = r.date.strftime('%Y-%m-%d %H:%M') if r.date else ''
            name = f"[{d}] {r.user_id.display_name} - {tdict.get(r.type, r.type)}"
            if r.reason:
                name += f" · {r.reason}"
            res.append((r.id, name))
        return res

    @api.model
    def log_entry(self, *, user=None, type_key=None, reason=None, ref_model=None, ref_id=None):
        """Permite llamadas con ref_model/ref_id; guarda en Reference."""
        if not type_key:
            return False
        user = user or self.env.user
        ref_val = f"{ref_model},{ref_id}" if (ref_model and ref_id) else False
        return self.sudo().create({
            "user_id": user.id,
            "type": type_key,
            "reason": reason or False,
            "ref": ref_val,
        })
