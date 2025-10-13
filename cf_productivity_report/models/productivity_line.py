# -*- coding: utf-8 -*-
from odoo import api, fields, models

class CFProductivityLine(models.Model):
    _name = "cf.productivity.line"
    _description = "CF Productividad - Registro"
    _order = "date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    date = fields.Datetime("Fecha", default=lambda self: fields.Datetime.now(), index=True)
    user_id = fields.Many2one("res.users", "Usuario", required=True, index=True)

# Métrica para pedidos/entregas
interval_minutes = fields.Integer(
    "Minutos desde última validación",
    default=0,
    index=True,
    help="Tiempo (en minutos) desde la última línea de tipo 'order' del mismo usuario. Se resetea si supera el timeout."
)
is_session_reset = fields.Boolean(
    "Reseteo por inactividad",
    default=False,
    help="Marcado si el intervalo superó el timeout configurado en la compañía."
)
    type = fields.Selection([
        ("repair", "Reparación"),
        ("ticket", "Ticket respondido"),
        ("order",  "Pedido/Entrega validada"),
    ], string="Tipo", required=True, index=True)
    reason = fields.Char("Motivo")
    ref_model = fields.Char("Modelo de referencia")
    ref_id = fields.Integer("ID referencia")

    def name_get(self):
        res = []
        for r in self:
            name = f"{r.user_id.name or '-'} - {dict(self._fields['type'].selection).get(r.type)}"
            res.append((r.id, name))
        return res

    
@api.model
def create(self, vals):
    rec = super(CFProductivityLine, self).create(vals)
    try:
        if rec.type == "order" and rec.user_id:
            timeout = rec.env.company.cf_order_timeout_min or 30
            # Última validación del mismo usuario y tipo
            last = self.search([
                ("id", "!=", rec.id),
                ("type", "=", "order"),
                ("user_id", "=", rec.user_id.id),
            ], order="date desc, id desc", limit=1)
            if last:
                diff = (fields.Datetime.from_string(rec.date) - fields.Datetime.from_string(last.date)).total_seconds() / 60.0
                if diff > timeout:
                    rec.write({"interval_minutes": 0, "is_session_reset": True})
                else:
                    rec.write({"interval_minutes": int(round(diff)), "is_session_reset": False})
            else:
                rec.write({"interval_minutes": 0, "is_session_reset": False})
    except Exception:
        pass
    return rec


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
